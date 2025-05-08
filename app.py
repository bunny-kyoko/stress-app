
import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import tempfile

st.set_page_config(page_title="ストレスチェックアプリ", layout="centered")

st.title("🧠 ストレスチェック・セルフケアレポート")

name = st.text_input("お名前（任意）", "")

st.markdown("### 以下の質問に、1（まったくそう思わない）～5（とてもそう思う）でお答えください。")

questions = {
    "A：仕事量・スピード": [
        "最近、仕事の量が多すぎると感じますか？",
        "時間に追われて仕事をすることが多いですか？",
        "休憩をとる時間がほとんどないと感じますか？"
    ],
    "B：役割・裁量・責任": [
        "自分の仕事の役割が不明確だと感じますか？",
        "仕事を進める裁量が少ないと感じますか？",
        "責任が重すぎると感じることがありますか？"
    ],
    "C：人間関係": [
        "上司に相談しにくいと感じますか？",
        "同僚との関係がうまくいっていないと感じますか？",
        "職場に孤独感を感じることがありますか？"
    ],
    "D：会社の支援体制": [
        "会社に相談できる人がいないと感じますか？",
        "会社のメンタル面の配慮が足りないと感じますか？",
        "職場に安心感や一体感を感じられないことがありますか？"
    ]
}

scores = {}
total_scores = {}

for category, qs in questions.items():
    st.subheader(category)
    score = 0
    for q in qs:
        val = st.slider(q, 1, 5, 3, key=q)
        score += val
    scores[category] = score

# レーダーチャート
if st.button("レポートを作成"):
    st.success("レポートを作成しました。以下からPDFをダウンロードできます。")
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    categories = list(scores.keys())
    values = list(scores.values())
    N = len(categories)
    values += values[:1]
    angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
    angles += angles[:1]
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # 一時ファイルに保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        tmpfile.write(buf.read())
        tmpfile_path = tmpfile.name

    # PDF生成
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("IPA", "", fname="ipaexg.ttf", uni=True)
    pdf.set_font("IPA", "", 14)
    pdf.cell(0, 10, "ストレスチェック個人レポート", ln=1)

    if name:
        pdf.set_font("IPA", "", 12)
        pdf.cell(0, 10, f"対象者：{name}", ln=1)

    pdf.set_font("IPA", "", 12)
    for k, v in scores.items():
        pdf.cell(0, 10, f"{k}：{v}点", ln=1)

    pdf.image(tmpfile_path, x=30, y=None, w=150)

    # アドバイス
    pdf.set_font("IPA", "", 11)
    pdf.ln(5)
    for k, v in scores.items():
        if v >= 10:
            pdf.multi_cell(0, 8, f"● {k} に関するアドバイス：")
            if k == "A：仕事量・スピード":
                pdf.multi_cell(0, 8, "- 小休憩を意識的に取り入れましょう")
                pdf.multi_cell(0, 8, "- 優先順位を明確にして取り組みましょう")
            elif k == "B：役割・裁量・責任":
                pdf.multi_cell(0, 8, "- 仕事の目的・役割を上司と確認しましょう")
                pdf.multi_cell(0, 8, "- 自分で決められるタスクを探しましょう")
            elif k == "C：人間関係":
                pdf.multi_cell(0, 8, "- 話しやすい同僚や信頼できる人に声をかけてみましょう")
                pdf.multi_cell(0, 8, "- チャットやメモでの相談も有効です")
            elif k == "D：会社の支援体制":
                pdf.multi_cell(0, 8, "- 産業医や外部相談窓口の活用を検討しましょう")
                pdf.multi_cell(0, 8, "- 制度や支援制度について調べてみましょう")
            pdf.ln(3)

    # ダウンロードボタン
    output = io.BytesIO()
    pdf.output(output)
    st.download_button("📄 PDFをダウンロード", data=output.getvalue(), file_name="stress_report.pdf", mime="application/pdf")
