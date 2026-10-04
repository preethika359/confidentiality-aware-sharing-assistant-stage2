from pathlib import Path
import pandas as pd
import streamlit as st

from modules.access_control import check_access, explain_decision, load_rules
from modules.detector import detect_sensitive_content
from modules.summarizer import generate_safe_summary
from modules.sharing import create_sharing_request, evaluate_sharing_request
from modules.audit import build_audit_row, append_audit

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
AUDIT_FILE = DATA_DIR / "audit_log.csv"

st.set_page_config(page_title="Confidentiality-Aware Sharing Assistant", page_icon="🔐", layout="wide")

if "sharing_request" not in st.session_state:
    st.session_state.sharing_request = None
if "sharing_result" not in st.session_state:
    st.session_state.sharing_result = None
if "override_reason" not in st.session_state:
    st.session_state.override_reason = ""


def audit(action, user_role, doc_id, title, target_role, decision, reason, evidence=None):
    """Write privacy-aware decision metadata; raw sensitive values are excluded."""
    row = build_audit_row(action, user_role, doc_id, title, target_role, decision, reason, evidence)
    append_audit(AUDIT_FILE, row)


@st.cache_data
def load_documents():
    """Load and validate the synthetic document schema before rendering the UI."""
    try:
        frame = pd.read_csv(DATA_DIR / "documents.csv")
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Document dataset cannot be loaded: {exc}") from exc
    required = {"document_id", "title", "permission_label", "content", "ground_truth_sensitive", "sensitive_category"}
    missing = required.difference(frame.columns)
    if missing:
        raise RuntimeError(f"Document dataset is missing required columns: {sorted(missing)}")
    return frame


try:
    documents = load_documents()
    rules = load_rules()
except RuntimeError as exc:
    st.error(f"Configuration/data error: {exc}")
    st.stop()

st.title("🔐 Confidentiality-Aware Summarisation & Sharing Assistant")
st.caption(f"Policy version: {rules.get('policy_version', 'unknown')} | Fail-closed access + human review for high-impact sharing")

user_role = st.sidebar.selectbox("👤 Current User Role", ["Student", "Faculty", "Admin"])

# Dashboard
st.header("📊 Safety Dashboard")
sensitive_count = sum(detect_sensitive_content(x)["sensitive"] for x in documents["content"])
cols = st.columns(4)
cols[0].metric("Documents", len(documents))
cols[1].metric("Restricted", int((documents.permission_label != "PUBLIC").sum()))
cols[2].metric("Sensitive", sensitive_count)
cols[3].metric("Roles", len(set(sum(rules["permission_levels"].values(), []))))

# Document selection
doc_title = st.selectbox("📄 Select document", documents["title"].tolist())
doc = documents[documents.title == doc_title].iloc[0]
doc_id, label, content = doc.document_id, doc.permission_label, doc.content
sensitive = detect_sensitive_content(content)
access = check_access(user_role, label)

c1, c2, c3 = st.columns(3)
c1.info(f"Document ID: {doc_id}")
c2.info(f"Permission: {label}")
c3.info(f"Sensitivity: {sensitive['severity']}")

st.header("🧠 Hybrid Sensitivity Detection")
layer_text = ", ".join(sensitive.get("layers", [])) or "none"
st.info(f"Detection layers: {layer_text} | Policy version: {rules.get('policy_version', 'unknown')}")
if sensitive.get("semantic_matches"):
    with st.expander("Semantic/context evidence"):
        st.dataframe(pd.DataFrame(sensitive["semantic_matches"]), width="stretch")

st.header("🔎 Access Decision")
if access["allowed"]:
    st.success("ACCESS ALLOWED")
else:
    st.error("ACCESS DENIED")

explanation = explain_decision(user_role, label, sensitive)
with st.expander("Why did the system decide this?", expanded=True):
    st.write(f"**Rule:** `{explanation['policy_rule']}`")
    st.write(f"**Authorised roles:** {', '.join(explanation['authorised_roles'])}")
    st.write(f"**Reason:** {explanation['reason']}")
    if explanation["sensitive_evidence"]:
        st.write("**Evidence detected:** " + ", ".join(explanation["sensitive_evidence"]))

if st.button("🔍 Record Access Decision"):
    audit("Document Access", user_role, doc_id, doc_title, "-", "Allowed" if access["allowed"] else "Denied", access["reason"], sensitive["items"])
    st.toast("Decision recorded in audit trail")

st.header("📝 Safe Summarisation")
if st.button("🧠 Generate Safe Summary"):
    if not access["allowed"]:
        summary = generate_safe_summary(user_role, content, sensitive, access_allowed=False)
        st.error(summary)
        audit("Safe Summarisation", user_role, doc_id, doc_title, "-", "Blocked", access["reason"], sensitive["items"])
    else:
        summary = generate_safe_summary(user_role, content, sensitive, access_allowed=True)
        st.success(summary)
        audit("Safe Summarisation", user_role, doc_id, doc_title, "-", "Allowed", "Summary generated under configured policy.", sensitive["items"])

st.header("📤 Controlled Sharing Workflow")
target_role = st.selectbox("Target role", ["Student", "Faculty", "Admin"], key="target_role")

if st.button("Create Sharing Request"):
    requester_access = check_access(user_role, label)
    target_access = check_access(target_role, label)
    request = create_sharing_request(user_role, doc_id, doc_title, target_role)
    result = evaluate_sharing_request(request, requester_access, target_access, sensitive)
    st.session_state.sharing_request = request
    st.session_state.sharing_result = result

if st.session_state.sharing_request:
    request = st.session_state.sharing_request
    result = st.session_state.sharing_result
    st.write(f"**Requester:** {request['requester_role']} → **Target:** {request['target_role']} → **Status:** {result['status']}")
    st.info(result["reason"])

    if result["status"] == "Review Required":
        st.warning("⚠️ High-impact action: human confirmation is mandatory.")
        confirmation = st.checkbox("I reviewed the request and confirm that sharing is appropriate.")
        reason = st.text_area("Mandatory override reason", placeholder="State why the sensitive document should be shared.")
        if st.button("🔓 Approve Manual Override"):
            if not confirmation:
                st.error("Human confirmation is required.")
            elif not reason.strip():
                st.error("Override reason is mandatory.")
            else:
                audit("Manual Override", user_role, doc_id, doc_title, target_role, "Approved", reason.strip(), sensitive["items"])
                st.success("Manual override approved and recorded.")
                st.session_state.sharing_request = None
                st.session_state.sharing_result = None
    elif result["status"] == "Blocked":
        audit("Sharing Request", user_role, doc_id, doc_title, target_role, "Blocked", result["reason"], sensitive["items"])
        st.error("Sharing blocked by policy.")
    else:
        audit("Sharing Request", user_role, doc_id, doc_title, target_role, "Approved", result["reason"], sensitive["items"])
        st.success("Sharing request approved by configured policy.")

st.header("📈 Evaluation Evidence")
metrics_path = ROOT / "experiments" / "metrics.json"
if metrics_path.exists():
    import json
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    m = st.columns(5)
    m[0].metric("Baseline leakage", f"{metrics['baseline_leakage_rate']*100:.2f}%")
    m[1].metric("Protected leakage", f"{metrics['protected_leakage_rate']*100:.2f}%")
    m[2].metric("Precision", f"{metrics['detector_precision']*100:.2f}%")
    m[3].metric("Recall", f"{metrics['detector_recall']*100:.2f}%")
    m[4].metric("F1", f"{metrics['detector_f1']*100:.2f}%")
    st.caption("Synthetic evaluation evidence; not a production security certification.")

st.header("🧾 Auditable Decision Trail")
if AUDIT_FILE.exists():
    audit_df = pd.read_csv(AUDIT_FILE)
    st.dataframe(audit_df, width="stretch")
    st.download_button("Download audit CSV", audit_df.to_csv(index=False), "audit_log.csv", "text/csv")
else:
    st.info("No audit decisions recorded yet.")

st.header("⚙️ Configured Policy")
st.json(rules)

st.header("📚 Document Inventory")
st.dataframe(documents[["document_id", "title", "permission_label"]], width="stretch")
