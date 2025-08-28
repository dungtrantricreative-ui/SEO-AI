import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Cấu hình Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Lỗi cấu hình Gemini: {e}")

# Giao diện web đơn giản (không thay đổi)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO YouTube Bá Đạo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
        h1 { color: #d90000; }
        #upload-form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input[type="file"], textarea { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { background-color: #ff0000; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        #loading, #result { margin-top: 20px; }
        pre { background: #eee; padding: 15px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h1>Tải Video Lên Để Tối Ưu SEO</h1>
    <form id="upload-form">
        <input type="file" id="video-file" name="video" accept="video/*" required>
        <textarea id="prompt" name="prompt" placeholder="Yêu cầu tùy chỉnh (bỏ trống để AI tự động)..."></textarea>
        <button type="submit">Tạo SEO ngay!</button>
    </form>
    <div id="loading" style="display:none;">Đang xử lý, vui lòng chờ...</div>
    <div id="result"></div>

    <script>
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const videoFile = document.getElementById('video-file').files[0];
            const userPrompt = document.getElementById('prompt').value;
            const loadingDiv = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            if (!videoFile) {
                resultDiv.innerHTML = "<p>Vui lòng chọn một video.</p>";
                return;
            }
            loadingDiv.style.display = 'block';
            resultDiv.innerHTML = '';
            const formData = new FormData();
            formData.append('video', videoFile);
            formData.append('prompt', userPrompt);
            try {
                const response = await fetch('/generate_seo', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.error) {
                    resultDiv.innerHTML = `<p><strong>Lỗi:</strong> ${data.error}</p>`;
                } else {
                    resultDiv.innerHTML = `<h2>Kết quả SEO:</h2><pre>${JSON.stringify(data, null, 2)}</pre>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p><strong>Lỗi kết nối:</strong> ${error.message}</p>`;
            } finally {
                loadingDiv.style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_seo', methods=['POST'])
def generate_seo_from_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    user_prompt = request.form.get('prompt', '')

    try:
        # --- ĐÃ THAY ĐỔI THEO YÊU CẦU CỦA BẠN ---
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        # --- KẾT THÚC THAY ĐỔI ---
        
        prompt = user_prompt if user_prompt else """
            Bạn là một chuyên gia SEO YouTube. Phân tích video này và tạo ra:
            1.  **suggested_titles**: 5 gợi ý tiêu đề hấp dẫn (dưới 70 ký tự).
            2.  **description**: Một đoạn mô tả chi tiết (tối thiểu 250 từ).
            3.  **tags**: Một danh sách 15 thẻ tags liên quan.
            Trả về kết quả dưới dạng một đối tượng JSON.
        """

        print("Sending video and prompt to the model...")
        response = model.generate_content([video_file, prompt])
        
        clean_response_text = response.text.replace('```json', '').replace('```', '').strip()
        return jsonify(json.loads(clean_response_text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
