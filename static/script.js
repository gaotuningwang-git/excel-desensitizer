// Excel数据脱敏工具 - 前端交互

document.addEventListener('DOMContentLoaded', function() {
    // 全局状态
    let currentFile = null;
    let currentFilename = null;
    let selectedColumns = [];

    // ===== 标签页切换 =====
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabId + '-panel').classList.add('active');
        });
    });

    // ===== 脱敏功能 =====

    // 文件上传
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // 处理文件上传
    function handleFileUpload(file) {
        if (!file.name.match(/\.(xlsx|xls)$/i)) {
            showError('只支持 .xlsx 和 .xls 格式的文件');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showLoading(true);
        hideError();

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.error) {
                showError(data.error);
                return;
            }

            currentFilename = data.filename;

            // 显示文件信息
            document.getElementById('file-name').textContent = file.name;
            document.getElementById('row-count').textContent = data.total_rows;
            document.getElementById('file-info').classList.remove('hidden');

            // 显示预览
            renderPreviewTable(data.preview, data.columns);
            document.getElementById('preview-section').classList.remove('hidden');

            // 显示列选择
            renderColumnCheckboxes(data.columns);
            document.getElementById('columns-section').classList.remove('hidden');
        })
        .catch(error => {
            showLoading(false);
            showError('上传失败: ' + error.message);
        });
    }

    // 渲染预览表格
    function renderPreviewTable(data, columns) {
        const table = document.getElementById('preview-table');
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');

        // 表头
        thead.innerHTML = '<tr>' + columns.map(function(col) { return '<th>' + escapeHtml(col) + '</th>'; }).join('') + '</tr>';

        // 表体
        tbody.innerHTML = data.map(function(row) {
            return '<tr>' + columns.map(function(col) {
                var val = row[col];
                if (val === null || val === undefined) val = '';
                return '<td>' + escapeHtml(String(val)) + '</td>';
            }).join('') + '</tr>';
        }).join('');
    }

    // 渲染列选择复选框
    function renderColumnCheckboxes(columns) {
        const container = document.getElementById('columns-list');
        container.innerHTML = columns.map(function(col) {
            return '<label class="column-checkbox">' +
                '<input type="checkbox" value="' + escapeHtml(col) + '" onchange="updateSelectedColumns(this)">' +
                '<span>' + escapeHtml(col) + '</span>' +
            '</label>';
        }).join('');

        selectedColumns = [];
        updateDesensitizeButton();
    }

    // 更新选中列
    window.updateSelectedColumns = function(checkbox) {
        const value = checkbox.value;
        const label = checkbox.closest('.column-checkbox');

        if (checkbox.checked) {
            selectedColumns.push(value);
            label.classList.add('checked');
        } else {
            selectedColumns = selectedColumns.filter(c => c !== value);
            label.classList.remove('checked');
        }

        updateDesensitizeButton();
    };

    // 更新脱敏按钮状态
    function updateDesensitizeButton() {
        const btn = document.getElementById('desensitize-btn');
        btn.disabled = selectedColumns.length === 0;
    }

    // 执行脱敏
    document.getElementById('desensitize-btn').addEventListener('click', () => {
        if (selectedColumns.length === 0) return;

        const mode = document.querySelector('input[name="mask-mode"]:checked').value;

        showLoading(true);
        hideError();

        fetch('/api/desensitize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentFilename,
                columns: selectedColumns,
                mode: mode
            })
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.error) {
                showError(data.error);
                return;
            }

            // 显示结果预览
            renderResultTable(data.preview);
            document.getElementById('result-section').classList.remove('hidden');

            // 设置下载链接
            document.getElementById('download-masked').href = data.download_urls.masked;
            document.getElementById('download-mapping').href = data.download_urls.mapping;

            showSuccess('脱敏处理完成！');

            // 滚动到结果区域
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            showLoading(false);
            showError('处理失败: ' + error.message);
        });
    });

    // 渲染结果表格
    function renderResultTable(data) {
        console.log('renderResultTable called with data:', data);
        if (!data || data.length === 0) {
            console.log('No data to render');
            return;
        }

        const columns = Object.keys(data[0]);
        console.log('Columns:', columns);

        const table = document.getElementById('result-table');
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');

        const headerHtml = '<tr>' + columns.map(function(col) { return '<th>' + escapeHtml(col) + '</th>'; }).join('') + '</tr>';
        console.log('Header HTML:', headerHtml);
        thead.innerHTML = headerHtml;

        const bodyHtml = data.map(function(row) {
            return '<tr>' + columns.map(function(col) {
                var val = row[col];
                if (val === null || val === undefined) val = '';
                return '<td>' + escapeHtml(String(val)) + '</td>';
            }).join('') + '</tr>';
        }).join('');
        console.log('Body HTML length:', bodyHtml.length);
        tbody.innerHTML = bodyHtml;
    }

    // ===== 还原功能 =====

    let maskedFile = null;
    let mappingFile = null;

    // 脱敏文件上传
    const uploadMasked = document.getElementById('upload-masked');
    const maskedInput = document.getElementById('masked-input');

    uploadMasked.addEventListener('click', () => maskedInput.click());
    maskedInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            maskedFile = e.target.files[0];
            document.getElementById('masked-filename').textContent = maskedFile.name;
            updateRestoreButton();
        }
    });

    // 对照表上传
    const uploadMapping = document.getElementById('upload-mapping');
    const mappingInput = document.getElementById('mapping-input');

    uploadMapping.addEventListener('click', () => mappingInput.click());
    mappingInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            mappingFile = e.target.files[0];
            document.getElementById('mapping-filename').textContent = mappingFile.name;
            updateRestoreButton();
        }
    });

    // 更新还原按钮状态
    function updateRestoreButton() {
        const btn = document.getElementById('restore-btn');
        btn.disabled = !(maskedFile && mappingFile);
    }

    // 执行还原
    document.getElementById('restore-btn').addEventListener('click', () => {
        if (!maskedFile || !mappingFile) return;

        const formData = new FormData();
        formData.append('masked_file', maskedFile);
        formData.append('mapping_file', mappingFile);

        showLoading(true);
        hideError();

        fetch('/api/restore', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.error) {
                showError(data.error);
                return;
            }

            // 显示还原结果
            renderRestoreResultTable(data.preview);
            document.getElementById('restore-result-section').classList.remove('hidden');

            // 设置下载链接
            document.getElementById('download-restored').href = data.download_url;

            showSuccess('数据还原完成！');

            // 滚动到结果区域
            document.getElementById('restore-result-section').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            showLoading(false);
            showError('还原失败: ' + error.message);
        });
    });

    // 渲染还原结果表格
    function renderRestoreResultTable(data) {
        if (!data || data.length === 0) return;

        const columns = Object.keys(data[0]);
        const table = document.getElementById('restore-result-table');
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');

        thead.innerHTML = '<tr>' + columns.map(function(col) { return '<th>' + escapeHtml(col) + '</th>'; }).join('') + '</tr>';
        tbody.innerHTML = data.map(function(row) {
            return '<tr>' + columns.map(function(col) {
                var val = row[col];
                if (val === null || val === undefined) val = '';
                return '<td>' + escapeHtml(String(val)) + '</td>';
            }).join('') + '</tr>';
        }).join('');
    }

    // ===== 工具函数 =====

    // 显示/隐藏加载状态
    function showLoading(show) {
        document.getElementById('loading').classList.toggle('hidden', !show);
    }

    // 显示错误信息
    function showError(message) {
        const el = document.getElementById('error-message');
        el.textContent = message;
        el.classList.remove('hidden');
        setTimeout(() => el.classList.add('hidden'), 5000);
    }

    // 隐藏错误信息
    function hideError() {
        document.getElementById('error-message').classList.add('hidden');
    }

    // 显示成功信息
    function showSuccess(message) {
        const el = document.getElementById('success-message');
        el.textContent = message;
        el.classList.remove('hidden');
        setTimeout(() => el.classList.add('hidden'), 3000);
    }

    // HTML转义
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
