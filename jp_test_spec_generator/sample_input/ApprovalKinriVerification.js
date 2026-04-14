'use strict';

(function () {
    let form = document.getElementById("ApprovalKinriVerification");

    /*
     * 登録ボタンのクリックイベント処理です。
     */
    const handleBtnRegistClick = function (e) {
        if (!e.isTrusted) {
            return;
        }
        e.preventDefault();

        // 共通チェック
        if (!bankr.validation.validateForm(form)) {
            bankr.dialog.showError('エラーが発生しました。入力内容を確認してください。');
            return;
        }

        bankr.dialog.showQuestion(WRIN5001, function (returnValue) {
            if (returnValue != 'ok') {
                return;
            }
            e.target.click();
        });
    };

    /*
     * 画面内容が変更された際に実行されます
     * フラグをfalseに設定し、隠しフィールドに値を同期します
     */
    const setPageChanged = function () {
        form.querySelector('#calculateFlgHidden').value = false;
    };

    /*
     * 画面内の全入力コントロールに変更イベントを設定します
     */
    const initChangeTracker = function () {
        // 対象コントロール：テキストボックス、ラジオボタン、ドロップダウンリスト、テキストエリア
        const inputElements = document.querySelectorAll(
            'input[type="text"], input[type="radio"], select, textarea'
        );

        inputElements.forEach(el => {
            el.addEventListener('change', setPageChanged);
            el.addEventListener('input', setPageChanged);
        });
    };

    /*
     * 口座番号テキストボックスの活性/非活性を設定します
     */
    const setAccountStatus = function () {
        const rbtNone = form.querySelector('#rbtNone');
        const rbtHave = form.querySelector('#rbtHave');

        if (!rbtNone || !rbtHave) return;

        // 口座番号テキストボックスを一括取得
        const accountInputs = form.querySelectorAll('[id^="tbxAccountNumber"]');
        const isReadOnly = rbtNone.checked;

        accountInputs.forEach(input => {
            if (isReadOnly) {
                input.value = "";
                input.setAttribute('data-readonly', true);
            } else {
                input.removeAttribute('data-readonly');
            }
        });
        // 返済条件合計金額取得
        const tbxRepaymentTermTotal = form.querySelector('#tbxRepaymentTermTotal');
        if (isReadOnly) {
            tbxRepaymentTermTotal.value = 0;
            tbxRepaymentTermTotal.setAttribute('data-readonly', true);
        } else {
            tbxRepaymentTermTotal.removeAttribute('data-readonly');
        }
    };

    /*
     * 口座番号制御の初期化
     */
    const initRepaymentTermControl = function () {
        const rbtNone = form.querySelector('#rbtNone');
        const rbtHave = form.querySelector('#rbtHave');

        if (rbtNone) rbtNone.addEventListener('change', setAccountStatus);
        if (rbtHave) rbtHave.addEventListener('change', setAccountStatus);

        // 初期表示時に1回実行
        setAccountStatus();
    };

    /*
     * 本件申請金利同期機能
     */
    const syncInterestRate = function () {
        // 申請金利テキストボックス
        const tbxInterestRate = form.querySelector('#tbxInterestRate');
        // 本件申請金利ラベル
        const lblApplicationIntrstRate = form.querySelector('#lblApplicationIntrstRate');

        if (!tbxInterestRate || !lblApplicationIntrstRate) return;

        // リアルタイムで同期
        const inputValue = tbxInterestRate.value.trim();
        // 空の場合、ラベルも空にする
        if (inputValue === '') {
            lblApplicationIntrstRate.textContent = '';
            return;
        }

        // 数値 → 3桁小数表示
        let val = parseFloat(inputValue) || 0;
        lblApplicationIntrstRate.textContent = val.toFixed(3);
    };

    // 本件申請金利同期機能の初期化
    const initInterestRateSync = function () {
        const tbxInterestRate = form.querySelector('#tbxInterestRate');

        if (tbxInterestRate) {
            // 入力するたびにリアルタイム反映
            tbxInterestRate.addEventListener('change', syncInterestRate);

            // 初期表示時に1回同期
            syncInterestRate();
        }
    };

    /*
     * 初期表示処理を実行します。
     */
    (function () {
        let target;

        // 登録ボタンのクリックイベント処理を割り当てます。
        target = form.querySelector('#btnRegist');
        if (target) {
            target.addEventListener('click', handleBtnRegistClick);
        }

        // 画面変更検知機能の初期化
        initChangeTracker();

        // 口座番号制御の初期化
        initRepaymentTermControl();

        // 本件申請金利同期機能の初期化
        initInterestRateSync();
    })();
})();
