"""
Excel数据脱敏工具 - Web界面
"""
import os
import sys
import uuid
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd

from desensitizer import ExcelDesensitizer

# 判断是否是打包后的 exe 运行
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后的路径
    BASE_DIR = Path(sys._MEIPASS)
else:
    # 开发环境路径
    BASE_DIR = Path(__file__).parent

app = Flask(__name__,
    template_folder=str(BASE_DIR / 'templates'),
    static_folder=str(BASE_DIR / 'static')
)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB

# 上传文件保存目录（使用用户目录，避免权限问题）
if getattr(sys, 'frozen', False):
    # 打包后使用用户临时目录
    APP_DATA_DIR = Path.home() / '.excel_desensitizer'
    UPLOAD_FOLDER = APP_DATA_DIR / 'uploads'
    RESULT_FOLDER = APP_DATA_DIR / 'results'
else:
    UPLOAD_FOLDER = Path('uploads')
    RESULT_FOLDER = Path('results')

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传Excel文件并返回列名"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '只支持 .xlsx 和 .xls 文件'}), 400

    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())[:8]
        filename = f"{file_id}_{secure_filename(file.filename)}"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)

        # 读取列名（所有列作为字符串处理，避免大数字溢出）
        df = pd.read_excel(filepath, dtype=str)
        columns = df.columns.tolist()

        # 预览前5行数据（将NaN替换为空字符串）
        preview = df.head(5).fillna('').to_dict('records')

        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'columns': columns,
            'preview': preview,
            'total_rows': len(df)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/desensitize', methods=['POST'])
def desensitize():
    """执行脱敏操作"""
    data = request.json
    filename = data.get('filename')
    columns = data.get('columns', [])
    mode = data.get('mode', 'mask')  # 'mask' 或 'full'

    if not filename or not columns:
        return jsonify({'error': '缺少参数'}), 400

    try:
        input_path = UPLOAD_FOLDER / filename
        result_id = str(uuid.uuid4())[:8]

        output_filename = f"masked_{result_id}.xlsx"
        mapping_filename = f"mapping_{result_id}.xlsx"
        output_path = RESULT_FOLDER / output_filename
        mapping_path = RESULT_FOLDER / mapping_filename

        # 执行脱敏
        desensitizer = ExcelDesensitizer()
        desensitizer.desensitize(
            input_path=str(input_path),
            output_path=str(output_path),
            mapping_path=str(mapping_path),
            columns=columns,
            keep_first_last=(mode == 'mask')
        )

        # 读取脱敏后的预览（所有列作为字符串处理）
        df_masked = pd.read_excel(output_path, dtype=str)
        preview = df_masked.head(5).fillna('').to_dict('records')

        return jsonify({
            'success': True,
            'result_id': result_id,
            'masked_file': output_filename,
            'mapping_file': mapping_filename,
            'preview': preview,
            'download_urls': {
                'masked': f'/api/download/masked/{output_filename}',
                'mapping': f'/api/download/mapping/{mapping_filename}'
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/restore', methods=['POST'])
def restore():
    """执行还原操作"""
    if 'masked_file' not in request.files or 'mapping_file' not in request.files:
        return jsonify({'error': '需要上传两个文件'}), 400

    masked_file = request.files['masked_file']
    mapping_file = request.files['mapping_file']

    if masked_file.filename == '' or mapping_file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    try:
        # 保存上传的文件
        result_id = str(uuid.uuid4())[:8]
        masked_filename = f"restore_masked_{result_id}.xlsx"
        mapping_filename = f"restore_mapping_{result_id}.xlsx"

        masked_path = UPLOAD_FOLDER / masked_filename
        mapping_path = UPLOAD_FOLDER / mapping_filename

        masked_file.save(masked_path)
        mapping_file.save(mapping_path)

        # 执行还原
        output_filename = f"restored_{result_id}.xlsx"
        output_path = RESULT_FOLDER / output_filename

        desensitizer = ExcelDesensitizer()
        desensitizer.restore(
            desensitized_path=str(masked_path),
            mapping_path=str(mapping_path),
            output_path=str(output_path)
        )

        # 读取还原后的预览（所有列作为字符串处理）
        df_restored = pd.read_excel(output_path, dtype=str)
        preview = df_restored.head(5).fillna('').to_dict('records')

        return jsonify({
            'success': True,
            'result_id': result_id,
            'restored_file': output_filename,
            'preview': preview,
            'download_url': f'/api/download/restored/{output_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<type>/<filename>')
def download_file(type, filename):
    """下载文件"""
    filepath = RESULT_FOLDER / filename
    if not filepath.exists():
        return jsonify({'error': '文件不存在'}), 404

    return send_file(filepath, as_attachment=True)


@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """清理临时文件"""
    try:
        # 清理上传文件
        for f in UPLOAD_FOLDER.glob('*'):
            f.unlink()
        # 清理结果文件
        for f in RESULT_FOLDER.glob('*'):
            f.unlink()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser(port):
    """延迟打开浏览器"""
    time.sleep(1.5)
    webbrowser.open(f'http://127.0.0.1:{port}')


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # 0 表示自动分配端口

    # 自动打开浏览器（仅在打包后运行）
    if getattr(sys, 'frozen', False):
        # 使用随机端口，避免冲突
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()

        # 后台线程打开浏览器
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    print(f"启动 Excel 数据脱敏工具...")
    print(f"请访问: http://127.0.0.1:{port}")
    print(f"上传目录: {UPLOAD_FOLDER}")
    print(f"结果目录: {RESULT_FOLDER}")
    print()

    # 关闭调试模式，避免打包后的问题
    app.run(debug=False, host='127.0.0.1', port=port)
