import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DB_PATH = "data/nifty100.db"
OUTPUT_DIR = "reports/radar_charts"

METRIC_LABELS = {
    "return_on_equity_pct_pctile": "ROE",
    "return_on_capital_pct_pctile": "ROCE",
    "net_profit_margin_pct_pctile": "NPM",
    "debt_to_equity_pctile": "D/E",
}


def load_peer_percentiles(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM peer_percentiles", conn)
    conn.close()
    return df


def plot_radar(company_id, company_values, group_avg_values, peer_group_name, output_dir=OUTPUT_DIR):
    labels = list(METRIC_LABELS.values())
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    company_vals = company_values + company_values[:1]
    group_vals = group_avg_values + group_avg_values[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, company_vals, linewidth=2, label=company_id, color="#2563eb")
    ax.fill(angles, company_vals, alpha=0.2, color="#2563eb")
    ax.plot(angles, group_vals, linewidth=2, linestyle="--", label="Peer Group Avg", color="#94a3b8")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_title(f"{company_id} vs {peer_group_name} Average", fontsize=11, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=8)

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{company_id}_radar.png")
    plt.savefig(filepath, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return filepath


def generate_all_radar_charts(db_path=DB_PATH, output_dir=OUTPUT_DIR):
    df = load_peer_percentiles(db_path)
    metric_cols = list(METRIC_LABELS.keys())

    generated = 0
    skipped = 0

    for peer_group_name, group_df in df.groupby("peer_group_name"):
        group_avg = [group_df[col].mean(skipna=True) for col in metric_cols]
        group_avg = [0 if pd.isna(v) else v for v in group_avg]

        for _, row in group_df.iterrows():
            company_vals = [row[col] for col in metric_cols]
            if all(pd.isna(v) for v in company_vals):
                skipped += 1
                continue
            company_vals = [0 if pd.isna(v) else v for v in company_vals]

            plot_radar(row["company_id"], company_vals, group_avg, peer_group_name, output_dir)
            generated += 1

    return generated, skipped


if __name__ == "__main__":
    print("Generating radar charts...")
    generated, skipped = generate_all_radar_charts()
    print(f"\nGenerated: {generated} charts")
    print(f"Skipped (no data): {skipped} companies")
    print(f"Saved to: {OUTPUT_DIR}/")