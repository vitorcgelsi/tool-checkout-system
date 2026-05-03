const STATUS_COLORS = {
  Available: "badge-green",
  "Checked Out": "badge-blue",
  Flagged: "badge-orange",
  "Under Maintenance": "badge-yellow",
  Missing: "badge-red",
  Retired: "badge-gray",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`badge ${STATUS_COLORS[status] || "badge-gray"}`}>
      {status}
    </span>
  );
}
