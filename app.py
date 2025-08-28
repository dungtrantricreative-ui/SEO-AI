import os
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Cấu hình Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Lỗi cấu hình Gemini: {e}")

# Giao diện web đã nâng cấp
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO YouTube Bá Đạo</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 800px; margin: auto; }
        h1 { color: #d90000; text-align: center; }
        .form-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        input[type="file"], textarea { display: block; width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
        button { background-color: #ff0000; color: white; padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: background-color 0.2s; }
        button:hover { background-color: #c00000; }
        #loading { text-align: center; margin-top: 20px; font-weight: bold; display: none; }
        .result-card { background: white; margin-top: 30px; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: none; }
        .result-section { margin-bottom: 25px; }
        .result-section h3 { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
        .copy-btn { float: right; background: #eee; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
        ul { list-style: none; padding-left: 0; }
        ul li { background: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 8px; }
        .tags-container { display: flex; flex-wrap: wrap; gap: 8px; }
        .tag { background: #e0e0e0; padding: 5px 12px; border-radius: 15px; font-size: 14px; }
        textarea.readonly-box { width: 100%; box-sizing: border-box; background-color: #f9f9f9; border: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SEO YouTube Bá Đạo 🚀</h1>
        <div class="form-card">
            <form id="upload-form">
                <input type="file" id="video-file" name="video" accept="video/*" required>
                <textarea id="prompt" name="prompt" rows="3" placeholder="Yêu cầu tùy chỉnh (bỏ trống để AI tự động)..."></textarea>
                <button type="submit">Tạo SEO ngay!</button>
            </form>
        </div>
        <div id="loading">Đang xử lý, vui lòng chờ...</div>
        <div id="result-card" class="result-card">
            </div>
    </div>

    <script>
        document.getElementById('upload-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const videoFile = document.getElementById('video-file').files[0];
            const userPrompt = document.getElementById('prompt').value;
            const loadingDiv = document.getElementById('loading');
            const resultCard = document.getElementById('result-card');

            if (!videoFile) { alert("Vui lòng chọn một video."); return; }

            loadingDiv.style.display = 'block';
            resultCard.style.display = 'none';
            resultCard.innerHTML = '';

            const formData = new FormData();
            formData.append('video', videoFile);
            formData.append('prompt', userPrompt);

            try {
                const response = await fetch('/generate_seo', { method: 'POST', body: formData });
                const data = await response.json();

                if (data.error) {
                    resultCard.innerHTML = `<p><strong>Lỗi:</strong> ${data.error}</p>`;
                } else {
                    displayResults(data);
                }
            } catch (error) {
                resultCard.innerHTML = `<p><strong>Lỗi kết nối:</strong> ${error.message}</p>`;
            } finally {
                loadingDiv.style.display = 'none';
                resultCard.style.display = 'block';
            }
        });

        function displayResults(data) {
            const resultCard = document.getElementById('result-card');
            
            // Tiêu đề
            let titlesHtml = '<ul>';
            if (data.suggested_titles && Array.isArray(data.suggested_titles)) {
                data.suggested_titles.forEach(title => { titlesHtml += `<li>${title}</li>`; });
            }
            titlesHtml += '</ul>';

            // Mô tả đầy đủ (kết hợp description, chapters, hashtags)
            let fullDescription = data.description || '';
            let chaptersText = '';
            if (data.chapters && Array.isArray(data.chapters) && data.chapters.length > 0) {
                chaptersText = data.chapters.join('\\n');
                fullDescription += '\\n\\n--- NỘI DUNG CHÍNH ---\\n' + chaptersText;
            }
            if (data.hashtags && Array.isArray(data.hashtags)) {
                fullDescription += '\\n\\n' + data.hashtags.join(' ');
            }
            
            // Thẻ Tags
            let tagsHtml = '<div class="tags-container">';
            if (data.tags && Array.isArray(data.tags)) {
                data.tags.forEach(tag => { tagsHtml += `<span class="tag">${tag}</span>`; });
            }
            tagsHtml += '</div>';

            resultCard.innerHTML = `
                <div class="result-section"><h3>💡 Tiêu đề gợi ý</h3>${titlesHtml}</div>
                <div class="result-section">
                    <h3>📝 Mô tả đầy đủ <button class="copy-btn" onclick="copyToClipboard('full-description-text')">Copy</button></h3>
                    <textarea id="full-description-text" rows="15" class="readonly-box" readonly>${fullDescription.replace(/\\n/g, '\\n')}</textarea>
                </div>
                <div class="result-section">
                    <h3>🏷️ Thẻ Tags (Từ khóa) <button class="copy-btn" onclick="copyToClipboard('tags-text', true)">Copy</button></h3>
                    ${tagsHtml}
                    <textarea id="tags-text" style="display:none;">${(data.tags || []).join(', ')}</textarea>
                </div>
            `;
        }

        function copyToClipboard(elementId, isTags = false) {
            const textToCopy = document.getElementById(elementId).value;
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert(isTags ? 'Đã copy các tags!' : 'Đã copy mô tả!');
            }).catch(err => { console.error('Lỗi khi copy: ', err); });
        }
    </script>
</body>
</html>
"""

# --- PHẦN BACKEND ĐƯỢC CẬP NHẬT ---
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
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        
        # --- CÂU LỆNH ẨN ĐÃ ĐƯỢC NÂNG CẤP ---
        prompt = user_prompt if user_prompt else """
            Bạn là một chuyên gia SEO YouTube. Phân tích kỹ lưỡng video này và tạo ra một đối tượng JSON với các key sau:
            1.  "suggested_titles": 5 gợi ý tiêu đề hấp dẫn (dưới 70 ký tự).
            2.  "description": Một đoạn mô tả chi tiết (tối thiểu 250 từ). Trong mô tả, hãy tự động chèn thêm một phần mẫu ở cuối cùng có dạng "[--- KÊNH LIÊN HỆ CỦA BẠN ---]" để người dùng tự điền thông tin mạng xã hội.
            3.  "chapters": Dựa vào các phần chính của video, hãy tạo ra các mốc thời gian (timestamps) theo định dạng "phút:giây - Tên chương". Bắt đầu bằng "00:00 - Giới thiệu".
            4.  "hashtags": Gợi ý 3-5 hashtag dạng "#Hashtag" súc tích, liên quan nhất đến nội dung video để đặt ở cuối mô tả.
            5.  "tags": Một danh sách 15 thẻ tags (từ khóa) để đưa vào phần tags của YouTube.
        """

        video_data = {
            'mime_type': video_file.mimetype,
            'data': video_file.read()
        }
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        print("Sending video and prompt to the model with safety settings off...")
        response = model.generate_content(
            [video_data, prompt],
            safety_settings=safety_settings
        )
        
        clean_response_text = response.text.replace('```json', '').replace('```', '').strip()
        
        if not clean_response_text:
            return jsonify({"error": "AI returned an empty response. The safety filter might have been triggered."}), 500
            
        return jsonify(json.loads(clean_response_text))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

