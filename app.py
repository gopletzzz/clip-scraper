import streamlit as st
import subprocess
import sys
import json
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Clip Scraper", layout="wide")
st.title("Clip Scraper")
st.info(
    "Catatan penting:\n\n"
    "• Bekerja optimal untuk Twitch \n\n"
    "• TikTok, kolom **Followers Count** akan kosong.\n\n"
    "• Reels, kolom **Username** yang ditampilkan adalah display name (bukan username).\n\n"
    "• Lainnya aman bang 😁😁😁😁"
)

st.write("Masukkan link video tiktok/short/reels/twitch. Satu link per baris.")

raw_links = st.text_area(
    "Input video links",
    height=200,
    placeholder="https://www.tiktok.com/@user/video/123\nhttps://www.tiktok.com/@user/video/456"
)

def get_video_meta(video_url):
    r = subprocess.run(
        [
            sys.executable, "-m", "yt_dlp",
            "--dump-single-json",
            "--user-agent", "Mozilla/5.0",
            video_url
        ],
        capture_output=True,
        text=True
    )
    if not r.stdout.strip():
        raise RuntimeError(r.stderr)
    return json.loads(r.stdout)

if st.button("Scrape"):
    links = [l.strip() for l in raw_links.splitlines() if l.strip()]

    if not links:
        st.error("Tidak ada link valid.")
    else:
        rows = []
        progress = st.progress(0)

        for i, link in enumerate(links):
            try:
                meta = get_video_meta(link)
            except Exception as e:
                st.warning(f"Gagal scrape: {link}")
                continue

            rows.append({
                "Clip Link": meta.get("webpage_url") or link,
                "Username": meta.get("uploader"),
                "Followers Count": meta.get("channel_follower_count"),
                "Clip Views Count": meta.get("view_count"),
                "Upload Date": (
                    datetime.strptime(meta["upload_date"], "%Y%m%d").date()
                    if meta.get("upload_date") else None
                ),
                "Caption": meta.get("description"),
                "likes": meta.get("like_count"),
            })

            progress.progress((i + 1) / len(links))

        if not rows:
            st.error("Tidak ada data berhasil diambil.")
        else:
            df = pd.DataFrame(rows)

            st.subheader("Output Table")
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False),
                file_name="clips.csv",
                mime="text/csv"
            )