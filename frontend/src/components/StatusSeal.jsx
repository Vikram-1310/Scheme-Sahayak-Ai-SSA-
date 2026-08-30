const LABELS = {
  true: { text: "Eligible", cls: "seal-eligible" },
  false: { text: "Not eligible", cls: "seal-not-eligible" },
};

// Accepts either a boolean `eligible` flag or a status string
// ("ELIGIBLE" / "NOT_ELIGIBLE" / "INSUFFICIENT_INFORMATION") since both
// shapes appear across the eligibility and recommendation endpoints.
export default function StatusSeal({ eligible, status }) {
  let text = "Unclear";
  let cls = "seal-unknown";

  if (typeof eligible === "boolean") {
    ({ text, cls } = LABELS[String(eligible)]);
  } else if (status) {
    if (status === "ELIGIBLE") ({ text, cls } = LABELS.true);
    else if (status === "NOT_ELIGIBLE") ({ text, cls } = LABELS.false);
    else text = "Needs more info";
  }

  return <span className={`seal ${cls}`}>{text}</span>;
}
