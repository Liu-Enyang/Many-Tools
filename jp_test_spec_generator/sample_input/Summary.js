'use strict';

(function () {

    const init = function () {

        /**
         * クリアボタン押下時処理
         * ・顧客番号クリア
         * ・顧客名クリア
         */
        let btnClear = document.querySelector('#btnClear');
        if (btnClear) {
            btnClear.addEventListener('click', function () {

                // 顧客番号クリア
                let customerNo = document.querySelector('#tbxCustomerNo');
                if (customerNo) customerNo.value = '';

                // 顧客名クリア
                let customerName = document.querySelector('#lblCustomerName');
                if (customerName) customerName.textContent = '';

            });
        }

        /**
         * 概況クリアボタン押下時処理
         * ・事故原因
         * ・現況
         * ・方針
         * ・備考
         */
        let btnSummaryClear = document.querySelector('#btnSummaryClear');
        if (btnSummaryClear) {
            btnSummaryClear.addEventListener('click', function () {

                // 事故および延滞に至った原因 クリア
                let txtReason = document.querySelector('#txtReason');
                if (txtReason) txtReason.value = '';

                // 債務者および保証人の現況 クリア
                let txtCurrentSituation = document.querySelector('#txtCurrentSituation');
                if (txtCurrentSituation) txtCurrentSituation.value = '';

                // 回収、解消の方針、スケジュール クリア
                let txtPolicy = document.querySelector('#txtPolicy');
                if (txtPolicy) txtPolicy.value = '';

                // 備考、特記事項 クリア
                let txtRemarks = document.querySelector('#txtRemarks');
                if (txtRemarks) txtRemarks.value = '';
            });
        }

        /**
         * 顧客検索ボタン押下時処理
         * ・顧客検索ダイアログ起動
         * ・選択した顧客番号／顧客名を画面へ反映
         */
        let btnCustSearch = document.querySelector('#btnCustSearch');
        if (btnCustSearch) {
            btnCustSearch.addEventListener('click', handleBtnCustSearchClick);
        }

        /**
         * 参照モード時の画面制御
         * ・リンク、ボタン、入力項目を操作不可にする
         */
        applyReferenceMode();

        // 帳票チェックボックス初期化
        initReportCheckBox();

        // 帳票ダウンロード初期化
        initReportDownload();

        // テーブルソート初期化
        initSort();
    };

    /**
     * 参照モード時の画面制御
     */
    const applyReferenceMode = function () {

        let hidReferenceMode = document.querySelector('#hidReferenceMode');
        if (!hidReferenceMode || hidReferenceMode.value !== '1') {
            return;
        }

        const elements = document.querySelectorAll('.js-disable-in-ref');

        elements.forEach(function (el) {
            const tag = el.tagName.toLowerCase();

            if (tag === 'input' || tag === 'button' || tag === 'select' || tag === 'textarea') {
                el.disabled = true;
            } else if (tag === 'a') {
                el.style.pointerEvents = 'none';
                el.style.color = '#999';
                el.addEventListener('click', function (e) {
                    e.preventDefault();
                    return false;
                });
            } else {
                el.style.pointerEvents = 'none';
            }
        });

        const childInputs = document.querySelectorAll('.js-disable-in-ref input, .js-disable-in-ref select, .js-disable-in-ref textarea, .js-disable-in-ref button');
        childInputs.forEach(function (el) {
            el.disabled = true;
        });

        const childLinks = document.querySelectorAll('.js-disable-in-ref a');
        childLinks.forEach(function (el) {
            el.style.pointerEvents = 'none';
            el.style.color = '#999';
            el.addEventListener('click', function (e) {
                e.preventDefault();
                return false;
            });
        });
    };

    /**
 * 帳票チェックボックス初期化
 * ・全選択 → 明細連動
 * ・明細全部選択 → 全選択自動ON
 * ・参照モード時は操作不可
 */
    const initReportCheckBox = function () {

        // ▼ WebForms の client id を考慮して suffix / contains で取得
        let chkAllReport =
            document.querySelector('input[id$="chkAllReport"]') ||
            document.querySelector('input[id*="chkAllReport"]');

        let reportChecks = Array.from(
            document.querySelectorAll('input[id*="chkReport_"]')
        );

        let hidReferenceMode = document.querySelector('#hidReferenceMode');
        let isReferenceMode = hidReferenceMode && hidReferenceMode.value === '1';

        if (!chkAllReport || reportChecks.length === 0) {
            return;
        }

        // ▼ 参照モード時は全て操作不可
        if (isReferenceMode) {
            chkAllReport.disabled = true;
            reportChecks.forEach(function (chk) {
                chk.disabled = true;
            });
            return;
        }

        // ▼ 全選択 → 明細連動
        chkAllReport.addEventListener('change', function () {
            reportChecks.forEach(function (chk) {
                chk.checked = chkAllReport.checked;
            });
        });

        // ▼ 明細全部選択 → 全選択自動ON / 一部解除でOFF
        reportChecks.forEach(function (chk) {
            chk.addEventListener('change', function () {
                let isAllChecked = reportChecks.every(function (item) {
                    return item.checked;
                });

                chkAllReport.checked = isAllChecked;
            });
        });

        // ▼ 初期表示時も状態同期
        chkAllReport.checked = reportChecks.every(function (item) {
            return item.checked;
        });
    };

    /**
     * 顧客検索ボタン押下時処理
     */
    const handleBtnCustSearchClick = function (e) {

        e.preventDefault();

        let hidReferenceMode = document.querySelector('#hidReferenceMode');
        if (hidReferenceMode && hidReferenceMode.value === '1') {
            return false;
        }

        let branch = document.querySelector('#ddlBranchNo');
        let customerNo = document.querySelector('#tbxCustomerNo');
        let customerName = document.querySelector('#lblCustomerName');

        if (!branch || !customerNo) {
            return;
        }

        let branchNo = branch.value || '';
        if (!branchNo) {
            if (typeof bankr !== 'undefined' && bankr.dialog && bankr.dialog.showError) {
                bankr.dialog.showError('店番・店名を選択してください。');
            } else {
                alert('店番・店名を選択してください。');
            }
            return;
        }

        let params = new URLSearchParams({
            Opener: 'COMMON',
            BranchNo: branchNo,
            Kijyunbi: ''
        });

        let url = '/RiskTaker/common/CustomerSelect.aspx?' + params.toString();

        bankr.dialog.open(url, function (returnValue) {
            if (!returnValue) {
                return;
            }

            let ret = returnValue;
            if (typeof returnValue === 'string') {
                try {
                    ret = JSON.parse(returnValue);
                } catch (err) {
                    return;
                }
            }

            if (!ret) {
                return;
            }

            if (ret.CustomerNo) {
                customerNo.value = ret.CustomerNo;
            }

            if (customerName) {
                customerName.textContent = ret.CustomerShortName || ret.CustomerName || '';
            }
        });
    };

    /**
     * 帳票ダウンロード初期化
     */
    const initReportDownload = function () {

        let btnDownload =
            document.querySelector('input[id$="btnDownload"]') ||
            document.querySelector('input[id*="btnDownload"]') ||
            document.querySelector('#btnDownload');
        if (!btnDownload) return;

        btnDownload.addEventListener('click', function (e) {

            e.preventDefault();

            // ▼ 顧客番号と店番を取得
            let customerNo = document.querySelector('#tbxCustomerNo');
            let branchNo = document.querySelector('#ddlBranchNo');

            // ▼ 顧客番号チェック
            if (!customerNo || !customerNo.value.trim()) {
                if (typeof bankr !== 'undefined' && bankr.dialog && bankr.dialog.showError) {
                    bankr.dialog.showError('顧客番号を入力してください。');
                } else {
                    alert('顧客番号を入力してください。');
                }
                return;
            }

            // ▼ 店番チェック
            if (!branchNo || !branchNo.value) {
                if (typeof bankr !== 'undefined' && bankr.dialog && bankr.dialog.showError) {
                    bankr.dialog.showError('店番・店名を選択してください。');
                } else {
                    alert('店番・店名を選択してください。');
                }
                return;
            }

            let form = document.forms[0];
            let checkedList = document.querySelectorAll('input[id*="chkReport"]:checked');
            let elementIds = [];
            let fileNames = [];
            let definitions = [];
            let count = 0;

            if (!checkedList || checkedList.length === 0) {
                if (typeof bankr !== 'undefined' && bankr.dialog && bankr.dialog.showError) {
                    bankr.dialog.showError('帳票を選択してください。');
                } else {
                    alert('帳票を選択してください。');
                }
                return;
            }

            checkedList.forEach(function (chk) {

                // ▼ 同一行取得
                let row = chk.closest('tr');
                if (!row) return;

                let elementIdNode = row.querySelector('input[id*="hidElementId"]');
                let fileNameNode = row.querySelector('input[id*="hidReportName"]');
                let definitionNode = row.querySelector('input[id*="hidDefinition"]');

                let elementId = elementIdNode ? elementIdNode.value : '';
                let fileName = fileNameNode ? fileNameNode.value : '';
                let definition = definitionNode ? definitionNode.value : '';

                if (!elementId || !fileName) {
                    return;
                }

                count++;
                elementIds.push(elementId);
                fileNames.push(encodeURIComponent(fileName));
                definitions.push(definition);
            });

            if (count === 0) {
                if (typeof bankr !== 'undefined' && bankr.dialog && bankr.dialog.showError) {
                    bankr.dialog.showError('帳票を選択してください。');
                } else {
                    alert('帳票を選択してください。');
                }
                return;
            }

            for (let j = 0; j < count; j++) {
                console.log('handleDownload: elementIds', elementIds[j]);
                console.log('handleDownload: fileNames', fileNames[j]);
                console.log('handleDownload: definitions', definitions[j]);
            }

            // ▼ 顧客番号・店番を画面から取得
            let url = '../common/DownLoadRSheet.aspx?elementId=' + elementIds.join('|')
                + '&fileName=' + fileNames.join('|')
                + '&Kind=RSHEET&Definition=' + definitions.join('|')
                + "&BranchNo=" + encodeURIComponent(branchNo.value.trim())
                + "&CustomerNo=" + encodeURIComponent(customerNo.value.trim());

            let down =
                document.querySelector('#downloadFrame');

            if (down) {
                down.src = url;
            } 

            return;
        });
    };

    /**
     * ソート初期化処理
     * ・data-sortable 属性を持つテーブルを対象にする
     * ・各列ヘッダクリックで昇順／降順を切り替える
     */
    const initSort = function () {

        // ▼ テーブル毎にソート状態を保持
        let sortState = {};

        // ▼ ソート対象テーブル取得
        const tables = document.querySelectorAll('table[data-sortable]');

        tables.forEach(table => {

            const tableId = table.id;
            sortState[tableId] = {};

            // ▼ ヘッダ取得
            const headers = table.querySelectorAll('thead th');

            headers.forEach((th, index) => {

                // ▼ data-sort が無い列は対象外
                if (!th.dataset.sort) return;

                th.style.cursor = 'pointer';

                th.addEventListener('click', function () {

                    // ▼ 列インデックス（data-col 優先）
                    let colIndex = th.dataset.col ? parseInt(th.dataset.col) : index;

                    // ▼ ソート種別（string / number / date）
                    let type = th.dataset.sort;

                    // ▼ 昇順／降順切替
                    let order = sortState[tableId][colIndex] === 'ASC' ? 'DESC' : 'ASC';
                    sortState[tableId][colIndex] = order;

                    sortTable(table, colIndex, type, order);
                });
            });
        });
    };

    /**
     * テーブルソート処理
     */
    const sortTable = function (table, colIndex, type, order) {

        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {

            let valA = getValue(a, colIndex, type);
            let valB = getValue(b, colIndex, type);

            if (valA < valB) return order === 'ASC' ? -1 : 1;
            if (valA > valB) return order === 'ASC' ? 1 : -1;
            return 0;
        });

        // ▼ 並び替え後、DOM再構築
        tbody.innerHTML = '';
        rows.forEach(r => tbody.appendChild(r));
    };

    /**
     * セル値取得処理
     * ・data-value があれば優先使用
     * ・日付は char(8)（yyyyMMdd）も対応
     */
    const getValue = function (row, index, type) {

        let cell = row.children[index];

        // ▼ data-value（生データ）があれば優先
        let raw = cell.getAttribute('data-value');

        switch (type) {

            /**
             * 数値
             */
            case 'number': {
                let text = raw || cell.innerText.trim();
                return parseFloat(text.replace(/,/g, '')) || 0;
            }

            /**
             * 日付
             */
            case 'date': {

                // ▼ char(8)（yyyyMMdd）優先
                if (raw && raw.length === 8) {
                    return parseDateRaw(raw);
                }

                // ▼ 表示文字列（yyyy/MM/dd）
                let text = cell.innerText.trim();
                return parseDateText(text);
            }

            /**
             * 文字列
             */
            default:
                return (raw || cell.innerText.trim());
        }
    };

    /**
     * yyyyMMdd → Date 変換
     */
    const parseDateRaw = function (text) {

        let y = parseInt(text.substring(0, 4));
        let m = parseInt(text.substring(4, 6)) - 1;
        let d = parseInt(text.substring(6, 8));

        return new Date(y, m, d);
    };

    /**
     * yyyy/MM/dd → Date 変換
     */
    const parseDateText = function (text) {

        if (!text) return new Date(0);

        let parts = text.split('/');

        if (parts.length !== 3) return new Date(0);

        let y = parseInt(parts[0]);
        let m = parseInt(parts[1]) - 1;
        let d = parseInt(parts[2]);

        return new Date(y, m, d);
    };

    document.addEventListener('DOMContentLoaded', init);

})();