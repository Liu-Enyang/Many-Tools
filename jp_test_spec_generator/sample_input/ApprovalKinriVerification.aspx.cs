using Isid.Copera.Util.Check;
using Isid.RiskTaker.Approval.Common;
using Isid.RiskTaker.Approval.Common.Message;
using Isid.RiskTaker.Approval.Common.UI;
using Isid.RiskTaker.Approval.Common.Utility;
using Isid.RiskTaker.Approval.Logic.Parameters;
using Isid.RiskTaker.Common.BusinessLogic;
using Isid.RiskTaker.Common.Utility;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Web.UI.WebControls;
using static Isid.RiskTaker.Approval.Persistence.DsApprovalKinriVerification;

namespace Isid.RiskTaker.Web
{
    /// <summary>
    /// 適正金利検証画面クラス。
    /// </summary>
    /// <remarks>
    /// <para>作成日 :2026/03/26</para>
    /// <para>作成者 : MS 陳俊魁</para>
	/// <para>変更履歴</para>
	/// <list type="bullet">
	/// <item>2026/03/26　MS 陳俊魁  RT-RT-73344_170.Chushin_【次世代融資支援PJ】No.32_適正金利表示</item>
	/// </list>
    /// </remarks>
    /// 
    public partial class ApprovalKinriVerification : ApprovalPage
    {
        #region クラスメンバー変数
        /// <summary>
        /// クラスメンバー変数：メッセージ出力用メンバー変数
        /// </summary>	
        private static readonly Isid.RiskTaker.Common.Message.IMessageManager messageManager = RiskTaker.Common.Message.MessageManager.GetInstance(MessageId_Approval.CATEGORY);

        /// <summary>
        /// クラスメンバー変数：入力チェックのエラーメッセージを設定する。
        /// </summary>
        private StringBuilder SbrErrItem;
        #endregion

        #region 定数宣言
        /// <summary>金利区分:変動金利</summary>
        private const string R_KINRINENGEN1 = "R_KINRINENGEN1";
        /// <summary>責任共有区分:負担金</summary>
        private const string R_RSPNSBLTY2 = "R_RSPNSBLTY2";
        /// <summary>責任共有区分:対象外</summary>
        private const string R_RSPNSBLTY9 = "R_RSPNSBLTY9";
        #endregion

        #region ビジネスロジックパラメータ取得用プロパティ
        /// <summary>
        /// 更新フラグ
        /// </summary>
        protected bool IsUpdate
        {
            get
            {
                return (bool)ViewState["IsUpdate"];
            }
            set
            {
                ViewState["IsUpdate"] = value;
            }
        }

        /// <summary>
        /// 事業性標準金利リストを設定取得します。
        /// </summary>
        public IDictionary<string, decimal> BusinessStdRateList
        {
            get
            {
                return ViewState["BusinessStdRateList"] as IDictionary<string, decimal>;
            }
            set
            {
                ViewState["BusinessStdRateList"] = value;
            }
        }

        /// <summary>
        /// 新規経費率を設定取得します。
        /// </summary>
        public decimal NewExpenseRate
        {
            get
            {
                return ViewState["NewExpenseRate"] == null ? 0m : (decimal)ViewState["NewExpenseRate"];
            }
            set
            {
                ViewState["NewExpenseRate"] = value;
            }
        }

        /// <summary>
        /// 市場金利を設定取得します。
        /// </summary>
        public decimal MarketInterestRate
        {
            get
            {
                return ViewState["MarketInterestRate"] == null ? 0m : (decimal)ViewState["MarketInterestRate"];
            }
            set
            {
                ViewState["MarketInterestRate"] = value;
            }
        }

        /// <summary>
        /// 倒産確率を設定取得します。
        /// </summary>
        public decimal BankruptcyRate
        {
            get
            {
                return ViewState["BankruptcyRate"] == null ? 0m : (decimal)ViewState["BankruptcyRate"];
            }
            set
            {
                ViewState["BankruptcyRate"] = value;
            }
        }

        /// <summary>
        /// 間接経費率を設定取得します。
        /// </summary>
        public decimal IndirectExpenseRate
        {
            get
            {
                return ViewState["IndirectExpenseRate"] == null ? 0m : (decimal)ViewState["IndirectExpenseRate"];
            }
            set
            {
                ViewState["IndirectExpenseRate"] = value;
            }
        }

        /// <summary>
        /// 収益スプレッドを設定取得します。
        /// </summary>
        public decimal RevenueSpread
        {
            get
            {
                return ViewState["RevenueSpread"] == null ? 0m : (decimal)ViewState["RevenueSpread"];
            }
            set
            {
                ViewState["RevenueSpread"] = value;
            }
        }

        /// <summary>
        /// 業種コードを設定取得します。
        /// </summary>
        public string GyosyuCode
        {
            get
            {
                return ViewState["GyosyuCode"] as string ?? string.Empty;
            }
            set
            {
                ViewState["GyosyuCode"] = value;
            }
        }

        /// <summary>
        /// 格付
        /// </summary>
        public string Grading
        {
            get
            {
                return (this.FindControl("ddlRGkvcGrading") as DropDownList).SelectedValue;
            }
        }

        /// <summary>
        /// 申請金額
        /// </summary>
        public string ApplicationMoney
        {
            get
            {
                return (this.FindControl("tbxExecScheduledMoney") as TextBox).Text;
            }
        }

        /// <summary>
        /// 申請金利
        /// </summary>
        public string ApplicationIntrstRate
        {
            get
            {
                return (this.FindControl("tbxInterestRate") as TextBox).Text;
            }
        }

        /// <summary>
        /// 資金使途
        /// </summary>
        public string CapitalUse
        {
            get
            {
                return (this.FindControl("ddlCapitalUseDivision") as DropDownList).SelectedValue;
            }
        }

        /// <summary>
        /// 金利年限
        /// </summary>
        public string KinriNengen
        {
            get
            {
                return (this.FindControl("ddlVariableInterestCode") as DropDownList).SelectedValue;
            }
        }

        /// <summary>
        /// 固定金利期間
        /// </summary>
        public string FixedIntstRatePeriod
        {
            get
            {
                return (this.FindControl("tbxFixedIntstRatePeriod") as TextBox).Text;
            }
        }

        /// <summary>
        /// 本件追加担保・保証時価格
        /// </summary>
        public string GuaranteeJika
        {
            get
            {
                return (this.FindControl("tbxGuaranteeJika") as TextBox).Text;
            }
        }

        /// <summary>
        /// 既存担保・保証時価余力額
        /// </summary>
        public string GuaranteeYoryoku
        {
            get
            {
                return (this.FindControl("tbxGuaranteeYoryoku") as TextBox).Text;
            }
        }

        /// <summary>
        /// 案件保全率
        /// </summary>
        public string CaseRetentionRate
        {
            get
            {
                return (this.FindControl("lblCaseRetentionRate") as Label).Text;
            }
        }

        /// <summary>
        /// 信用コスト（計算式）
        /// </summary>
        public string ShinyoCostShiki
        {
            get
            {
                return (this.FindControl("lblShinyoCostShiki") as Label).Text;
            }
        }

        /// <summary>
        /// 採用標準金利
        /// </summary>
        public string StdInterestRate
        {
            get
            {
                return (this.FindControl("lblStandardIntrstRate") as Label).Text;
            }
        }

        /// <summary>
        /// 採用標準金利（計算式）
        /// </summary>
        public string StdInterestRateShiki
        {
            get
            {
                return (this.FindControl("lblStdInterestRateShiki") as Label).Text;
            }
        }

        /// <summary>
        /// 貸出金利
        /// </summary>
        public string LoanInterestRate
        {
            get
            {
                return (this.FindControl("lblCalculateInterestRate") as Label).Text;
            }
        }

        /// <summary>
        /// 貸出金利（計算式）
        /// </summary>
        public string LoanInterestRateShiki
        {
            get
            {
                return (this.FindControl("lblOutputArea") as Label).Text;
            }
        }

        /// <summary>
        /// 乖離幅
        /// </summary>
        public string DeviationRange
        {
            get
            {
                return (this.FindControl("lblDeviationRange") as Label).Text;
            }
        }

        /// <summary>
        /// 所見
        /// </summary>
        public string Findings
        {
            get
            {
                return (this.FindControl("tbxFindings") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件の有無
        /// </summary>
        public short RepaymentTermFlg
        {
            get
            {
                var rbtHave = this.FindControl("rbtHave") as RadioButton;
                // 1:有、2：無
                if (rbtHave.Checked)
                {
                    return 1;
                }
                return 2;
            }
        }

        /// <summary>
        /// 返済条件（1）口座番号
        /// </summary>
        public string AccountNumber1
        {
            get
            {
                return (this.FindControl("tbxAccountNumber1") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（2）口座番号
        /// </summary>
        public string AccountNumber2
        {
            get
            {
                return (this.FindControl("tbxAccountNumber2") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（3）口座番号
        /// </summary>
        public string AccountNumber3
        {
            get
            {
                return (this.FindControl("tbxAccountNumber3") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（4）口座番号
        /// </summary>
        public string AccountNumber4
        {
            get
            {
                return (this.FindControl("tbxAccountNumber4") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（5）口座番号
        /// </summary>
        public string AccountNumber5
        {
            get
            {
                return (this.FindControl("tbxAccountNumber5") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（6）口座番号
        /// </summary>
        public string AccountNumber6
        {
            get
            {
                return (this.FindControl("tbxAccountNumber6") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（7）口座番号
        /// </summary>
        public string AccountNumber7
        {
            get
            {
                return (this.FindControl("tbxAccountNumber7") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（8）口座番号
        /// </summary>
        public string AccountNumber8
        {
            get
            {
                return (this.FindControl("tbxAccountNumber8") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（9）口座番号
        /// </summary>
        public string AccountNumber9
        {
            get
            {
                return (this.FindControl("tbxAccountNumber9") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件（10）口座番号
        /// </summary>
        public string AccountNumber10
        {
            get
            {
                return (this.FindControl("tbxAccountNumber10") as TextBox).Text;
            }
        }

        /// <summary>
        /// 返済条件合計金額
        /// </summary>
        public string RepaymentTermTotal
        {
            get
            {
                return (this.FindControl("tbxRepaymentTermTotal") as TextBox).Text;
            }
        }

        /// <summary>
        /// 貸出期間（月数）
        /// </summary>
        public string LoanPeriod
        {
            get
            {
                return (this.FindControl("tbxLoanPeriod") as TextBox).Text;
            }
        }

        /// <summary>
        /// 真水金額
        /// </summary>
        public string MamizuMoney
        {
            get
            {
                return (this.FindControl("lblMamizuMoney") as Label).Text;
            }
        }

        /// <summary>
        /// 貸出金利収益
        /// </summary>
        public string LoanKinriSyueki
        {
            get
            {
                return (this.FindControl("lblLoanKinriSyueki") as Label).Text;
            }
        }

        /// <summary>
        /// 本件計算内容
        /// </summary>
        public string CalculationDetails
        {
            get
            {
                return (this.FindControl("lblCalculationDetails") as Label).Text;
            }
        }
        #endregion

        #region Web Form Designer generated code
        /// <summary>
        /// 画面クラスの初期化を行う。
        /// </summary>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        override protected void OnInit(EventArgs e)
        {
            //
            // CODEGEN: この呼び出しは、ASP.NET Web フォーム デザイナで必要です。
            //
            InitializeComponent();
            base.OnInit(e);
        }

        /// <summary>
        /// Designer サポートに必要なメソッドです。コード エディタで
        /// このメソッドのコンテンツを変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            this.MessagePreRender += new Isid.RiskTaker.Approval.Common.UI.PresentationBase.MessagePreRenderEventHandler(this.Page_MessagePreRender);
        }

        /// <summary>
        /// スクリプトメッセージID出力イベントの処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生したオブジェクト</param>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>登録ボタン押下時の確認メッセージを出力設定する。</item>
        /// </list>
        /// </remarks>
        private void Page_MessagePreRender(object sender, Isid.RiskTaker.Common.Message.MessagePreRenderEventArgs e)
        {
            Hashtable hstRegist = new Hashtable();
            hstRegist.Add("text", "登録");
            e.AddMessage(MessageId_Approval.WRIN5001, hstRegist);
        }
        #endregion

        #region Page_Load
        /// <summary>
        /// Page.Loadイベントの処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生したオブジェクト</param>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!this.IsPostBack)
            {
                // 表示モード設定
                //this.SetDisplayMode();

                // 拡張FWで使用する画面モード
                string screenMode = "WRITE";

                // 排他制御確認
                if (this.ApprovalInformation.AuthorityMode == Constant.AuthorityModeType.WaitEntry)
                {
                    // 画面モードを参照モードに
                    screenMode = "READ";

                    // 排他ロック状態に対応するメッセージの出力
                    this.AppendExclusivePrivilegesMessage(this.ExclusivePrivileges);
                }
                else
                {
                    // 表示状態変更
                    switch (this.DisplayMode)
                    {
                        case Constant.DisplayModeType.Entry:
                        case Constant.DisplayModeType.Update:
                            screenMode = "WRITE";
                            break;
                        default:
                            screenMode = "READ";
                            break;
                    }
                }

                // ViewStateに保持
                this.ScreenMode = screenMode;

                // 表示状態切替
                this.SetupControl(this.ScreenMode);

                // 格付のDropDownList設定
                this.BindGenericCodeToDropDownList(ddlRGkvcGrading, "KAKUDUKE", false, true);
                // 金利区分のDropDownList設定
                this.BindGenericCodeToDropDownList(ddlVariableInterestCode, "R_KINRINENGEN", false, true);
                // 資金使途のDropDownList設定
                this.BindGenericCodeToDropDownList(ddlCapitalUseDivision, "R_SIKINSITOM", true, true);

                // 表示処理
                this.Display();
            }
        }
        #endregion

        #region 表示処理
        /// <summary>
        /// DBよりデータを取得して画面に表示する。
        /// </summary>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>クラスを使用してDBよりデータを取得する。</item>
        /// <item>コントロールへデータを設定する。</item>
        /// </list>
        /// </remarks>
        private void Display()
        {
            ApprovalKinriVerificationInitializeParameter p
                = (ApprovalKinriVerificationInitializeParameter)this.CreateParameter("W090_001");
            using (ILogic logic = (ILogic)this.CreateLogic("W090_001"))
            {
                try
                {
                    if (!logic.Execute(p))
                    {
                        // エラーあり
                        this.AppendMessage(p.Messages);
                        // 表示状態を"READ"に切り替える
                        this.SetupControlState("READ");
                        return;
                    }
                    // データの表示
                    this.DisplayData(p);
                }
                catch (LogicException ex)
                {
                    // 業務プロセスエラー
                    this.AppendMessage(Isid.RiskTaker.Common.Constant.MessageAreaLevel.BusinessError, ex.Message);
                    // 表示状態を"READ"に切り替える
                    this.SetupControlState("READ");
                }
            }
        }

        /// <summary>
        /// 画面表示処理
        /// </summary>
        /// <param name="p">パラメータオブジェクト</param>
        private void DisplayData(ApprovalKinriVerificationInitializeParameter p)
        {
            // 更新判断
            if (p.IsUpdate)
            {
                // 適正金利検証情報(断面)の表示
                this.DispShowProperInterestRate(p);
                // 更新フラグ
                this.IsUpdate = true;
            }
            else
            {
                // 基本条件等の入力内容の表示
                this.DispBasicConditionInput(p);
                // 更新フラグ
                this.IsUpdate = false;
            }

            // 計算フラグ
            this.calculateFlgHidden.Value = "False";
            // 新規経費率
            this.NewExpenseRate = p.NewExpenseRate;
            // 市場金利
            this.MarketInterestRate = p.MarketInterestRate;
            // 倒産確率
            this.BankruptcyRate = p.BankruptcyRate;
            // 間接経費率
            this.IndirectExpenseRate = p.IndirectExpenseRate;
            // 収益スプレッド
            this.RevenueSpread = p.RevenueSpread;
            // 業種コード
            this.GyosyuCode = p.GyosyuCode;

            // 事業性標準金利リスト
            this.BusinessStdRateList = new Dictionary<string, decimal>();
            for (int i = 0; i < p.DataSet.spApprovalKinriVerification_sel06.Count; i++)
            {
                this.BusinessStdRateList.Add(p.DataSet.spApprovalKinriVerification_sel06[i].RMbsr_KinriNengen,
                    p.DataSet.spApprovalKinriVerification_sel06[i].RMbsr_BusinessStdRate);
            }

        }
        #endregion

        #region 適正金利検証情報(断面)の表示処理
        /// <summary>
        /// 適正金利検証情報(断面)の表示処理
        /// </summary>
        /// <param name="p">パラメータオブジェクト</param>
        private void DispShowProperInterestRate(ApprovalKinriVerificationInitializeParameter p)
        {
            if (p.DataSet.spApprovalKinriVerification_sel02.Count > 0)
            {
                // データ表示
                spApprovalKinriVerification_sel02Row sel02Row = p.DataSet.spApprovalKinriVerification_sel02[0];

                // 格付
                if (!sel02Row.IsRGkvc_GradingNull())
                {
                    this.ddlRGkvcGrading.SelectedValue = sel02Row.RGkvc_Grading;
                }

                // 申請金額
                if (!sel02Row.IsRGkvc_ApplicationMoneyNull())
                {
                    this.tbxExecScheduledMoney.Text = Util.Currency(sel02Row.RGkvc_ApplicationMoney);
                }

                // 申請金利
                if (!sel02Row.IsRGkvc_ApplicationIntrstRateNull())
                {
                    this.tbxInterestRate.Text = Dec2Str(sel02Row.RGkvc_ApplicationIntrstRate, 3);
                }

                // 資金使途
                if (!sel02Row.IsRGkvc_CapitalUseNull())
                {
                    this.ddlCapitalUseDivision.SelectedValue = sel02Row.RGkvc_CapitalUse;
                }

                // 収益スプレッド
                if (!sel02Row.IsRGkvc_RevenueSpreadNull())
                {
                    this.lblRevenueSpread.Text = Dec2Str(sel02Row.RGkvc_RevenueSpread, 3);
                }

                // 金利年限
                if (!sel02Row.IsRGkvc_KinriNengenNull())
                {
                    this.ddlVariableInterestCode.SelectedValue = sel02Row.RGkvc_KinriNengen;
                }

                // 固定金利期間
                if (!sel02Row.IsRGkvc_FixedIntstRatePeriodNull())
                {
                    this.tbxFixedIntstRatePeriod.Text = sel02Row.RGkvc_FixedIntstRatePeriod;
                }

                // 本件追加担保・保証時価格
                if (!sel02Row.IsRGkvc_GuaranteeJikaNull())
                {
                    this.tbxGuaranteeJika.Text = Util.Currency(sel02Row.RGkvc_GuaranteeJika);
                }

                // 既存担保・保証時価余力額
                if (!sel02Row.IsRGkvc_GuaranteeYoryokuNull())
                {
                    this.tbxGuaranteeYoryoku.Text = Util.Currency(sel02Row.RGkvc_GuaranteeYoryoku);
                }

                // 案件保全率
                if (!sel02Row.IsRGkvc_CaseRetentionRateNull())
                {
                    this.lblCaseRetentionRate.Text = Dec2Str(sel02Row.RGkvc_CaseRetentionRate, 3);
                }

                // 信用コスト（計算式）
                if (!sel02Row.IsRGkvc_ShinyoCostShikiNull())
                {
                    this.lblShinyoCostShiki.Text = sel02Row.RGkvc_ShinyoCostShiki;
                }

                // 採用標準金利
                if (!sel02Row.IsRGkvc_StdInterestRateNull())
                {
                    this.lblStandardIntrstRate.Text = Dec2Str(sel02Row.RGkvc_StdInterestRate, 3);
                }

                // 採用標準金利（計算式）
                if (!sel02Row.IsRGkvc_StdInterestRateShikiNull())
                {
                    this.lblStdInterestRateShiki.Text = sel02Row.RGkvc_StdInterestRateShiki;
                }

                // 貸出金利
                if (!sel02Row.IsRGkvc_LoanInterestRateNull())
                {
                    this.lblCalculateInterestRate.Text = Dec2Str(sel02Row.RGkvc_LoanInterestRate, 3);
                }

                // 貸出金利（計算式）
                if (!sel02Row.IsRGkvc_LoanInterestRateShikiNull())
                {
                    this.lblOutputArea.Text = sel02Row.RGkvc_LoanInterestRateShiki;
                }

                // 乖離幅
                if (!sel02Row.IsRGkvc_DeviationRangeNull())
                {
                    this.lblDeviationRange.Text = Dec2Str(sel02Row.RGkvc_DeviationRange, 3);
                }

                // 所見
                if (!sel02Row.IsRGkvc_FindingsNull())
                {
                    this.tbxFindings.Text = sel02Row.RGkvc_Findings;
                }

                // 返済条件の有無
                if (!sel02Row.IsRGkvc_RepaymentTermFlgNull())
                {
                    if (sel02Row.RGkvc_RepaymentTermFlg == 1)
                    {
                        this.rbtHave.Checked = true;
                    }
                    else
                    {
                        this.rbtNone.Checked = true;
                    }
                }

                // 返済条件（1）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber1Null())
                {
                    this.tbxAccountNumber1.Text = sel02Row.RGkvc_AccountNumber1;
                }

                // 返済条件（2）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber2Null())
                {
                    this.tbxAccountNumber2.Text = sel02Row.RGkvc_AccountNumber2;
                }

                // 返済条件（3）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber3Null())
                {
                    this.tbxAccountNumber3.Text = sel02Row.RGkvc_AccountNumber3;
                }

                // 返済条件（4）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber4Null())
                {
                    this.tbxAccountNumber4.Text = sel02Row.RGkvc_AccountNumber4;
                }

                // 返済条件（5）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber5Null())
                {
                    this.tbxAccountNumber5.Text = sel02Row.RGkvc_AccountNumber5;
                }

                // 返済条件（6）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber6Null())
                {
                    this.tbxAccountNumber6.Text = sel02Row.RGkvc_AccountNumber6;
                }

                // 返済条件（7）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber7Null())
                {
                    this.tbxAccountNumber7.Text = sel02Row.RGkvc_AccountNumber7;
                }

                // 返済条件（8）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber8Null())
                {
                    this.tbxAccountNumber8.Text = sel02Row.RGkvc_AccountNumber8;
                }

                // 返済条件（9）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber9Null())
                {
                    this.tbxAccountNumber9.Text = sel02Row.RGkvc_AccountNumber9;
                }

                // 返済条件（10）口座番号
                if (!sel02Row.IsRGkvc_AccountNumber10Null())
                {
                    this.tbxAccountNumber10.Text = sel02Row.RGkvc_AccountNumber10;
                }

                // 返済条件合計金額
                if (!sel02Row.IsRGkvc_RepaymentTermTotalNull())
                {
                    this.tbxRepaymentTermTotal.Text = Util.Currency(sel02Row.RGkvc_RepaymentTermTotal);
                }

                // 貸出期間（月数）
                if (!sel02Row.IsRGkvc_LoanPeriodNull())
                {
                    this.tbxLoanPeriod.Text = sel02Row.RGkvc_LoanPeriod;
                }

                // 真水金額
                if (!sel02Row.IsRGkvc_MamizuMoneyNull())
                {
                    this.lblMamizuMoney.Text = Util.Currency(sel02Row.RGkvc_MamizuMoney);
                }

                // 貸出金利収益
                if (!sel02Row.IsRGkvc_LoanKinriSyuekiNull())
                {
                    this.lblLoanKinriSyueki.Text = Util.Currency(sel02Row.RGkvc_LoanKinriSyueki);
                }

                // 本件計算内容
                if (!sel02Row.IsRGkvc_CalculationDetailsNull())
                {
                    this.lblCalculationDetails.Text = sel02Row.RGkvc_CalculationDetails;
                }
            }
        }
        #endregion

        #region 基本条件等の入力内容の表示処理
        /// <summary>
        /// 基本条件等の入力内容の表示処理
        /// </summary>
        /// <param name="p">パラメータオブジェクト</param>
        private void DispBasicConditionInput(ApprovalKinriVerificationInitializeParameter p)
        {
            if (p.DataSet.spApprovalKinriVerification_sel03.Count > 0)
            {
                // データ表示
                spApprovalKinriVerification_sel03Row sel03Row = p.DataSet.spApprovalKinriVerification_sel03[0];

                // 格付
                if (!Util.IsEmpty(p.Grading))
                {
                    this.ddlRGkvcGrading.SelectedValue = p.Grading;
                }

                // 申請金額
                if (!sel03Row.IsRGlap_ExecScheduledMoneyNull())
                {
                    this.tbxExecScheduledMoney.Text = Util.Currency(sel03Row.RGlap_ExecScheduledMoney);
                }

                // 申請金利
                if (!sel03Row.IsRGlap_InterestRateNull())
                {
                    this.tbxInterestRate.Text = Dec2Str(sel03Row.RGlap_InterestRate, 3);
                }

                // 資金使途
                if (!Util.IsEmpty(sel03Row.RGlap_CapitalUseDetailDivision))
                {
                    this.ddlCapitalUseDivision.SelectedValue = sel03Row.RGlap_CapitalUseDetailDivision;
                }

                // 収益スプレッド
                this.lblRevenueSpread.Text = Dec2Str(p.RevenueSpread, 3);

                // 金利区分
                ddlVariableInterestCode.SelectedIndex = 0;

                // 本件追加担保・保証時価額
                // 基本条件画面．保証機関コードに入力あり、かつ2000以上(しんきん保証基金など)
                if (!Util.IsEmpty(sel03Row.RGlap_SecurityCode) && Util.Str2Int(sel03Row.RGlap_SecurityCode) >= 2000)
                {
                    // 申込金額 / 1000
                    if (!sel03Row.IsRGlap_ExecScheduledMoneyNull())
                    {
                        this.tbxGuaranteeJika.Text = Util.Currency(sel03Row.RGlap_ExecScheduledMoney);
                    }

                }
                // 基本条件画面．保証機関コードに入力あり、かつ 1000～1999(協会 / 一般 京都など) かつ 基本条件画面．責任共有区分が「負担金」
                else if (!Util.IsEmpty(sel03Row.RGlap_SecurityCode)
                    && Util.Str2Int(sel03Row.RGlap_SecurityCode) >= 1000
                    && Util.Str2Int(sel03Row.RGlap_SecurityCode) <= 1999
                    && !sel03Row.IsRGlap_RespShareDivisionNull()
                    && R_RSPNSBLTY2.Equals(sel03Row.RGlap_RespShareDivision))
                {
                    //（申込金額×80％）/1000
                    if (!sel03Row.IsRGlap_ExecScheduledMoneyNull())
                    {
                        this.tbxGuaranteeJika.Text = Util.Currency(sel03Row.RGlap_ExecScheduledMoney * 0.8m);
                    }
                }
                // 基本条件画面．保証機関コードに入力あり、かつ 1000～1999かつ 基本条件画面．責任共有区分が「対象外」
                else if (!Util.IsEmpty(sel03Row.RGlap_SecurityCode)
                    && Util.Str2Int(sel03Row.RGlap_SecurityCode) >= 1000
                    && Util.Str2Int(sel03Row.RGlap_SecurityCode) <= 1999
                    && !sel03Row.IsRGlap_RespShareDivisionNull()
                    && R_RSPNSBLTY9.Equals(sel03Row.RGlap_RespShareDivision))
                {
                    // 申込金額 / 1000
                    if (!sel03Row.IsRGlap_ExecScheduledMoneyNull())
                    {
                        this.tbxGuaranteeJika.Text = Util.Currency(sel03Row.RGlap_ExecScheduledMoney);
                    }
                }
                // 取引状況画面．根担保時価取分または不動産担保時価取分の「i:今回増減」に入力有
                else if (sel03Row.RGepr_RealEstateRootSecurity + sel03Row.RGepr_RealEstateMortgage > 0)
                {
                    // 根担保時価取分および不動産担保時価取分の「i:今回増減」の入力値合計/1000
                    this.tbxGuaranteeJika.Text = Util.Currency(sel03Row.RGepr_RealEstateRootSecurity + sel03Row.RGepr_RealEstateMortgage);
                }

                // 返済条件の有無
                // 基本条件の「借区分替」が選択されている場合
                if (!Util.IsEmpty(sel03Row.RGlap_RefinanceDivision))
                {
                    this.rbtHave.Checked = true;
                }
                else
                {
                    this.rbtNone.Checked = true;
                }

                // 口座番号と返済条件合計金額
                decimal repaymentTermTotalAll = 0;
                for (int i = 0; i < p.DataSet.spApprovalKinriVerification_sel05.Count; i++)
                {
                    TextBox tbxAccountNumber = (TextBox)this.FindControl("tbxAccountNumber" + (i + 1));
                    tbxAccountNumber.Text = p.DataSet.spApprovalKinriVerification_sel05[i].RGrcl_ShinseiNo;

                    repaymentTermTotalAll += p.DataSet.spApprovalKinriVerification_sel05[i].RGrcl_KasitukeZandaka;
                }

                // 返済条件合計金額に残高の合計を表示
                tbxRepaymentTermTotal.Text = Util.Currency(repaymentTermTotalAll);

                // 貸出期間（月数）
                if (!Util.IsEmpty(sel03Row.RGlap_ExecScheduledDate) && !Util.IsEmpty(sel03Row.RGlap_RepaymentLimitDay))
                {
                    // 実行予定日～最終返済期日までの月数
                    DateTime dtmStartDate = Util.Str2Datetime(sel03Row.RGlap_ExecScheduledDate);
                    DateTime dtmEndDate = Util.Str2Datetime(sel03Row.RGlap_RepaymentLimitDay);
                    int totalMonths = (dtmEndDate.Year - dtmStartDate.Year) * 12 + dtmEndDate.Month - dtmStartDate.Month;
                    if (dtmEndDate.Day < dtmStartDate.Day) totalMonths--;

                    this.tbxLoanPeriod.Text = totalMonths.ToString();
                }
            }
        }
        #endregion

        #region クリアボタン処理
        /// <summary>
        /// クリアボタン押下の処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生したオブジェクト</param>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>多重サブミットチェック。</item>
        /// <item>当画面の初期表示状態に戻る。</item>
        /// </list>
        /// </remarks>
        protected void btnClear_Click(object sender, System.EventArgs e)
        {
            // 多重サブミットチェック
            if (this.IsReRequest)
            {
                return;
            }

            // 計算結果を画面に空白表示する
            this.DoClearCalculateData();

            // 表示処理
            this.Display();

        }
        #endregion

        #region 計算結果を画面に空白表示する
        /// <summary>
        /// 計算結果を画面に空白表示する。
        /// </summary>
        /// <returns>なし</returns>
        private void DoClearCalculateData()
        {
            // 格付
            this.ddlRGkvcGrading.SelectedIndex = 0;
            // 申請金額
            this.tbxExecScheduledMoney.Text = string.Empty;
            // 申請金利
            this.tbxInterestRate.Text = string.Empty;
            // 資金使途
            this.ddlCapitalUseDivision.SelectedIndex = 0;
            // 金利区分
            this.ddlVariableInterestCode.SelectedIndex = 0;
            // 固定金利期間
            this.tbxFixedIntstRatePeriod.Text = string.Empty;
            // 本件追加担保・保証時価額
            this.tbxGuaranteeJika.Text = string.Empty;
            // 既存担保・保証時価余力額
            this.tbxGuaranteeYoryoku.Text = string.Empty;
            // 案件保全率（時価ベース）
            this.lblCaseRetentionRate.Text = string.Empty;
            // 採用標準金利
            this.lblStandardIntrstRate.Text = string.Empty;
            // 貸出金利
            this.lblCalculateInterestRate.Text = string.Empty;
            // 算出式の出力エリア
            this.lblOutputArea.Text = string.Empty;
            // 本件申請金利
            this.lblApplicationIntrstRate.Text = string.Empty;
            // 乖離幅
            this.lblDeviationRange.Text = string.Empty;
            // 所見
            this.tbxFindings.Text = string.Empty;
            // 返済条件の有無
            this.rbtNone.Checked = false;
            this.rbtHave.Checked = false;
            // 返済条件（1）口座番号
            this.tbxAccountNumber1.Text = string.Empty;
            // 返済条件（2）口座番号
            this.tbxAccountNumber2.Text = string.Empty;
            // 返済条件（3）口座番号
            this.tbxAccountNumber3.Text = string.Empty;
            // 返済条件（4）口座番号
            this.tbxAccountNumber4.Text = string.Empty;
            // 返済条件（5）口座番号
            this.tbxAccountNumber5.Text = string.Empty;
            // 返済条件（6）口座番号
            this.tbxAccountNumber6.Text = string.Empty;
            // 返済条件（7）口座番号
            this.tbxAccountNumber7.Text = string.Empty;
            // 返済条件（8）口座番号
            this.tbxAccountNumber8.Text = string.Empty;
            // 返済条件（9）口座番号
            this.tbxAccountNumber9.Text = string.Empty;
            // 返済条件（10）口座番号
            this.tbxAccountNumber10.Text = string.Empty;
            // 返済条件合計金額
            this.tbxRepaymentTermTotal.Text = string.Empty;
            // 貸出期間（月数）
            this.tbxLoanPeriod.Text = string.Empty;
            // 真水金額
            this.lblMamizuMoney.Text = string.Empty;
            // 貸出金利収益
            this.lblLoanKinriSyueki.Text = string.Empty;
            // 本件
            this.lblCalculationDetails.Text = string.Empty;
        }
        #endregion

        #region 計算ボタン押下の処理を行う
        /// <summary>
        /// 計算ボタン押下の処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生したオブジェクト</param>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>多重サブミットチェック。</item>
        /// <item>入力データの有効性チェックを行う。
        /// <para>－チェックエラーの場合は、エラーメッセージを表示する。</para>
        /// </item>
        /// <item>計算対象項目の計算を行う、計算結果を画面に表示する。</item>
        /// </list>
        /// </remarks>
        protected void btnCalculate_Click(object sender, System.EventArgs e)
        {
            // 多重サブミットチェック
            if (this.IsReRequest)
            {
                return;
            }

            // チェックの成功時
            if (CalculateCheck())
            {
                // 収益スプレッド最新化
                this.lblRevenueSpread.Text = Dec2Str(this.RevenueSpread, 3);
                // 計算対象項目の計算処理
                this.CalculateExecute();
                // 計算フラグ
                this.calculateFlgHidden.Value = "True";
            }
        }

        /// <summary>
        /// 計算対象項目の計算処理
        /// </summary>
        private void CalculateExecute()
        {
            // 本件追加担保・保証時価額
            decimal guaranteeJika = Util.Str2EnDecimal(tbxGuaranteeJika.Text);
            // 既存担保・保証時価余力額
            decimal guaranteeYoryoku = Util.Str2EnDecimal(tbxGuaranteeYoryoku.Text);
            // 申請金額
            decimal execScheduledMoney = Util.Str2EnDecimal(tbxExecScheduledMoney.Text);
            // 申請金利
            decimal interestRate = Util.ToDecimal(tbxInterestRate.Text);
            // 返済条件合計金額
            decimal repaymentTermTotal = Util.Str2EnDecimal(tbxRepaymentTermTotal.Text);
            // 貸出期間
            int loanPeriod = Util.Str2Int(tbxLoanPeriod.Text);
            // 事業性標準金利（金利区分毎）
            decimal businessStdRate = this.BusinessStdRateList[ddlVariableInterestCode.SelectedValue];

            // 安件保全率 = ｛（本件追加担保・保証時価額＋既存担保・保証時価余力額）／申請金額｝＊100
            decimal caseRetentionRate = (guaranteeJika + guaranteeYoryoku) / execScheduledMoney * 100;

            // 採用標準金利 = 事業性標準金利（金利区分毎）＋　新規経費率
            decimal standardIntrstRate = businessStdRate + this.NewExpenseRate;

            // 採用標準金利の計算式
            string stdInterestRateShiki = Dec2Str(businessStdRate, 3) + "%＋"
                + Dec2Str(this.NewExpenseRate, 3) + "% ⇒ "
                + Dec2Str(standardIntrstRate, 3) + "%";

            // 案件毎信用コスト=｛（100-案件保全率）* 倒産確率｝/100］
            decimal creditCostPerCase = (100 - caseRetentionRate) * this.BankruptcyRate / 100;

            // 案件毎信用コストの計算式
            string shinyoCostShiki = "{(100-" + Dec2Str(caseRetentionRate, 3) + ")*"
                + Dec2Str(this.BankruptcyRate, 3) + "%}/100 ⇒ "
                + Dec2Str(creditCostPerCase, 3) + "%";

            // 業種・資金使途・エリア要件
            decimal areaRequirement = CalculateAreaRequirement();

            // 貸出金利 = 標準金利＋案件毎信用コスト＋間接経費率＋収益スプレッド＋業種・資金使途・エリア要件
            decimal calculateInterestRate = standardIntrstRate + creditCostPerCase + this.IndirectExpenseRate + this.RevenueSpread + areaRequirement;

            // 貸出金利の計算式
            string outputArea = Dec2Str(standardIntrstRate, 3) + "+[{(100-"
                + Dec2Str(caseRetentionRate, 3) + ")*"
                + Dec2Str(this.BankruptcyRate, 3) + "}/100]+"
                + Dec2Str(this.IndirectExpenseRate, 3) + "+"
                + Dec2Str(this.RevenueSpread, 3) + "+"
                + Dec2Str(areaRequirement, 1);

            // 乖離幅 = 貸出金利 - 申請金利
            decimal deviationRange = calculateInterestRate - interestRate;

            // 真水金額 = 申請金額 - 返済条件合計金額
            decimal mamizuMoney = execScheduledMoney - repaymentTermTotal;

            // 貸出金利収益
            decimal loanKinriSyueki;
            // 貸出金利収益の計算式
            string calculationDetails;

            // 貸出期間が12ヶ月未満の場合
            if (loanPeriod < 12)
            {
                //貸出金利収益＝｛（申請金額－返済条件合計金額）×申請金利｝×貸出期間/12
                loanKinriSyueki = (execScheduledMoney - repaymentTermTotal) * interestRate / 100 * loanPeriod / 12;
                // 貸出金利収益の計算式
                calculationDetails = "{(" + Math.Round(execScheduledMoney).ToString() + "－"
                    + Math.Round(repaymentTermTotal).ToString() + ")×"
                    + Dec2Str(interestRate, 3) + "%}×" + loanPeriod.ToString() + "/12";
            }
            else
            {
                // 貸出金利収益＝（申請金額－返済条件合計金額）×評定対象金利
                // ※評定対象金利＝申請金利－事業性標準金利（金利区分毎）－案件毎の信用コスト－業種・資金使途・エリア要件
                loanKinriSyueki = (execScheduledMoney - repaymentTermTotal)
                    * (interestRate - businessStdRate - creditCostPerCase - areaRequirement) / 100;

                // 貸出金利収益の計算式
                calculationDetails = "(" + Math.Round(execScheduledMoney).ToString() + "－"
                    + Math.Round(repaymentTermTotal).ToString() + ")×("
                    + Dec2Str(interestRate, 3) + "%－"
                    + Dec2Str(businessStdRate, 3) + "%－"
                    + Dec2Str(creditCostPerCase, 3) + "%－"
                    + Dec2Str(areaRequirement, 3) + "%)";
                calculationDetails = calculationDetails + "<br>＝"
                    + "(" + Math.Round(execScheduledMoney).ToString() + "－"
                    + Math.Round(repaymentTermTotal).ToString() + ")×("
                    + Dec2Str(interestRate - businessStdRate - creditCostPerCase - areaRequirement, 3) + "%)";
            }

            // 計算結果を画面に表示
            lblCaseRetentionRate.Text = Dec2Str(caseRetentionRate, 3);           // 安件保全率
            lblStandardIntrstRate.Text = Dec2Str(standardIntrstRate, 3);         // 採用標準金利
            lblShinyoCostShiki.Text = "＝" + shinyoCostShiki;                    // 案件毎信用コストの計算式
            lblStdInterestRateShiki.Text = "＝" + stdInterestRateShiki;          // 採用標準金利の計算式
            lblCalculateInterestRate.Text = Dec2Str(calculateInterestRate, 3);   // 貸出金利
            lblOutputArea.Text = outputArea;                                     // 貸出金利の計算式
            lblDeviationRange.Text = Dec2Str(deviationRange, 3);                 // 乖離幅
            lblMamizuMoney.Text = mamizuMoney.ToString("#,##0");                 // 真水金額
            lblLoanKinriSyueki.Text = loanKinriSyueki.ToString("#,##0");         // 貸出金利収益
            lblCalculationDetails.Text = calculationDetails;                     // 本件

        }
        #endregion

        #region 業種・資金使途・エリア要件算出処理
        /// <summary>
        /// 業種・資金使途・エリア要件算出処理
        /// </summary>
        /// <returns>算出業種・資金使途・エリア要件</returns>
        private decimal CalculateAreaRequirement()
        {
            // 業種・資金使途・エリア要件
            decimal resultScore;
            // 業種コード
            string gyosyuCode = this.GyosyuCode;
            // 資金使途コード
            string capitalUse = RespectiveConfiguration.GetCodeValueBase(this.ddlCapitalUseDivision.SelectedValue, "R_SIKINSITOM");
            // 店番
            string branchNo = this.ApprovalInformation.CustomerInformation.BranchNo;

            // =====================================================================
            // ① 特定業種・特定資金使途に該当する場合
            // =====================================================================

            // 設定定義.業種コード１
            // 2600（建設業）、4100（不動産業）
            HashSet<string> gyosyuCodeList1 = new HashSet<string> { "2600", "4100" };

            // 設定定義.業種コード２
            // 4130（不動産賃貸業）、4150（個人による貸家業）
            HashSet<string> gyosyuCodeList2 = new HashSet<string> { "4130", "4150" };

            // 設定定義.資金使途コード１
            // 126（商品土地購入（更地））、127（商品建物建築）、128（商品土地・建物（戸建・ﾏﾝｼｮﾝ・ﾃﾅﾝﾄ））
            HashSet<string> capitalUseList1 = new HashSet<string> { "126", "127", "128" };

            // 設定定義.資金使途コード２
            // 238（新規起業設備②賃貸用土地建物購入（創業）（副業））、
            // 239（新規起業設備③賃貸集合住宅取得･建築･増改築･補修(創業)(副業)）、
            // 244（賃貸集合住宅取得・建築・増改築・補修）、245（賃貸用建物用地購入）、
            // 246（賃貸建物建築）、
            // 247（賃貸建物補修・改築）、
            // 248（賃貸建物・土地購入（戸建、テナント等））
            HashSet<string> capitalUseList2 = new HashSet<string> { "238", "239", "244", "245", "246", "247", "248" };

            // 業種コード＝設定定義.業種コード１ の場合
            if (gyosyuCodeList1.Contains(gyosyuCode))
            {
                resultScore = 0.2m;
            }
            // 業種コード＝設定定義.業種コード２の場合
            else if (gyosyuCodeList2.Contains(gyosyuCode))
            {
                // 資金使途コード＝設定定義.資金使途コード１の場合
                if (capitalUseList1.Contains(capitalUse))
                {
                    resultScore = 0.2m;
                }
                // 資金使途コード≠設定定義.資金使途コード１の場合
                else
                {
                    resultScore = 0.1m;
                }
            }
            // 業種コード≠設定定義.業種コード２ かつ 資金使途コード＝設定定義.資金使途コード１の場合
            else if (capitalUseList1.Contains(capitalUse))
            {
                resultScore = 0.2m;
            }
            // 業種コード≠設定定義.業種コード２ かつ 資金使途コード＝設定定義.資金使途コード２の場合
            else if (capitalUseList2.Contains(capitalUse))
            {
                resultScore = 0.1m;
            }
            // 上記以外の場合
            else
            {
                resultScore = 0m;
            }

            // =====================================================================
            // ②特定エリアの店舗の場合
            // =====================================================================
            // 特定店番
            HashSet<string> branchNoList = new HashSet<string>
                {
                    // 大阪府店舗
                    "31", "138", "143", "149", "151", "153", "155", "156", "157", "158",
                    // 奈良県店舗
                    "144", "152", "154"
                };

            // 特定店舗に該当する場合、0.2を加算
            if (branchNoList.Contains(branchNo))
            {
                resultScore += 0.2m;
            }
            return resultScore;
        }
        #endregion

        #region 計算ボタン押下時チェック処理
        /// <summary>
        /// 計算ボタン押下時チェックを行う。
        /// </summary>
        /// <returns>入力項目チェックの結果(true:正常、false:エラー)</returns>
        /// <remarks>
        /// 入力項目をチェックする。
        /// </remarks>
        private bool CalculateCheck()
        {
            bool blResult;
            string strItemName;
            SbrErrItem = new StringBuilder();

            // 共通チェック
            blResult = this.CommonCheck();

            // 返済条件有無未選択の場合
            strItemName = "返済条件有無";
            if (!(rbtNone.Checked || rbtHave.Checked))
            {
                // "返済条件有無は選択必須です。"
                SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5004));
                blResult = false;
            }

            // 口座番号
            if (rbtHave.Checked)
            {
                strItemName = "口座番号";
                // 口座番号が未入力の場合
                if (Util.IsEmpty(tbxAccountNumber1.Text) &&
                    Util.IsEmpty(tbxAccountNumber2.Text) &&
                    Util.IsEmpty(tbxAccountNumber3.Text) &&
                    Util.IsEmpty(tbxAccountNumber4.Text) &&
                    Util.IsEmpty(tbxAccountNumber5.Text) &&
                    Util.IsEmpty(tbxAccountNumber6.Text) &&
                    Util.IsEmpty(tbxAccountNumber7.Text) &&
                    Util.IsEmpty(tbxAccountNumber8.Text) &&
                    Util.IsEmpty(tbxAccountNumber9.Text) &&
                    Util.IsEmpty(tbxAccountNumber10.Text))
                {
                    // "口座番号は必須入力です。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                }
                else
                {
                    // 口座番号チェック
                    CheckResult chkResult1 = CheckValue.CheckLongType(tbxAccountNumber1.Text);
                    CheckResult chkResult2 = CheckValue.CheckLongType(tbxAccountNumber2.Text);
                    CheckResult chkResult3 = CheckValue.CheckLongType(tbxAccountNumber3.Text);
                    CheckResult chkResult4 = CheckValue.CheckLongType(tbxAccountNumber4.Text);
                    CheckResult chkResult5 = CheckValue.CheckLongType(tbxAccountNumber5.Text);
                    CheckResult chkResult6 = CheckValue.CheckLongType(tbxAccountNumber6.Text);
                    CheckResult chkResult7 = CheckValue.CheckLongType(tbxAccountNumber7.Text);
                    CheckResult chkResult8 = CheckValue.CheckLongType(tbxAccountNumber8.Text);
                    CheckResult chkResult9 = CheckValue.CheckLongType(tbxAccountNumber9.Text);
                    CheckResult chkResult10 = CheckValue.CheckLongType(tbxAccountNumber10.Text);

                    // 各項目のチェック結果の設定
                    CheckResult[] chkResult = new CheckResult[10]
                        { chkResult1, chkResult2, chkResult3, chkResult4, chkResult5, chkResult6, chkResult7, chkResult8, chkResult9, chkResult10 };

                    // 口座番号に全角、文字、記号が入力されている場合
                    if (chkResult.Any(x => x == CheckResult.ERROR))
                    {
                        // "口座番号は半角数字で入力してください。"
                        SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                        blResult = false;
                    }
                }
            }

            // 貸出期間（月数）
            strItemName = "貸出期間（月数）";
            switch (CheckValue.CheckIntRange(1, tbxLoanPeriod.Text, 999))
            {
                case (CheckResult.NULL):
                case (CheckResult.BLANK):
                    // {0}は必須入力です。
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                    break;
                case (CheckResult.ERROR):
                    // "{0}は半角数字で入力してください。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                    blResult = false;
                    break;
                case (CheckResult.HIGH):
                case (CheckResult.LOW):
                    // "貸出期間（月数）は1から999までの範囲値で入力してください。"
                    SbrErrItem.Append(GetErrorRangeMessage(strItemName, "1", "999", MessageId_Approval.ERIN5008));
                    blResult = false;
                    break;
                default:
                    break;
            }

            if (!blResult)
            {
                // メッセージエリアにメッセージ出力
                messageBox.PrintError(SbrErrItem.ToString());
            }
            return blResult;
        }
        #endregion

        #region 登録ボタン押下時チェック処理
        /// <summary>
        /// 登録ボタン押下時チェックを行う。
        /// </summary>
        /// <returns>入力項目チェックの結果(true:正常、false:エラー)</returns>
        /// <remarks>
        /// 入力項目をチェックする。
        /// </remarks>
        private bool RegistCheck()
        {
            bool blResult;
            SbrErrItem = new StringBuilder();

            // 共通チェック
            blResult = this.CommonCheck();

            // 計算ボタンを押下していない場合
            if (!Convert.ToBoolean(calculateFlgHidden.Value))
            {
                // "先に計算処理を行ってください。"
                string strMsg = Util.GetMessage(messageManager, MessageId_Approval.WRIN5062);
                SbrErrItem.Append(strMsg);
                blResult = false;
            }
            else
            {
                // 乖離幅が0以上かつ所見が未入力の場合
                if (Util.ToDecimal(lblDeviationRange.Text) > 0 && Util.IsEmpty(tbxFindings.Text))
                {
                    // "所見は必須入力です。"
                    SbrErrItem.Append(GetErrorMessage("所見", MessageId_Approval.ERIN5010));
                    blResult = false;
                }
            }

            if (!blResult)
            {
                // メッセージエリアにメッセージ出力
                messageBox.PrintError(SbrErrItem.ToString());
            }
            return blResult;
        }
        #endregion

        #region 共通チェック処理
        /// <summary>
        /// 共通チェックを行う。
        /// </summary>
        /// <returns>入力項目チェックの結果(true:正常、false:エラー)</returns>
        /// <remarks>
        /// 入力項目をチェックする。
        /// </remarks>
        private bool CommonCheck()
        {
            bool blResult = true;
            string strItemName;

            // 金利区分
            strItemName = "金利区分";
            // 必須入力チェック
            if (ddlVariableInterestCode.SelectedIndex == 0)
            {
                // {0}は必須入力です。
                SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                blResult = false;
            }

            // 格付
            strItemName = "格付";
            // 必須入力チェック
            if (ddlRGkvcGrading.SelectedIndex == 0)
            {
                // {0}は必須入力です。
                SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                blResult = false;
            }

            // 資金使途
            strItemName = "資金使途";
            // 必須入力チェック
            if (ddlCapitalUseDivision.SelectedIndex == 0)
            {
                // {0}は必須入力です。
                SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                blResult = false;
            }

            // 申請金額
            strItemName = "申請金額";
            bool blCheckExecScheduledMoney = false;
            switch (CheckValue.CheckDecimalRange(1m, tbxExecScheduledMoney.Text, 9999999m))
            {
                case (CheckResult.NULL):
                case (CheckResult.BLANK):
                    // {0}は必須入力です。
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                    break;
                case (CheckResult.ERROR):
                    // "{0}は半角数字で入力してください。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                    blResult = false;
                    break;
                case (CheckResult.HIGH):
                case (CheckResult.LOW):
                    // "申請金額は1から9,999,999までの範囲値で入力してください。"
                    SbrErrItem.Append(GetErrorRangeMessage(strItemName, "1", "9,999,999", MessageId_Approval.ERIN5008));
                    blResult = false;
                    break;
                case (CheckResult.NORMAL):
                    blCheckExecScheduledMoney = true;
                    break;
                default:
                    break;
            }

            // 本件追加担保・保証時価額
            strItemName = "本件追加担保・保証時価額";
            bool blCheckGuaranteeJika = false;
            switch (CheckValue.CheckDecimalRange(0, tbxGuaranteeJika.Text, 9999999m))
            {
                case (CheckResult.NULL):
                case (CheckResult.BLANK):
                    // {0}は必須入力です。
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                    break;
                case (CheckResult.ERROR):
                    // "{0}は半角数字で入力してください。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                    blResult = false;
                    break;
                case (CheckResult.HIGH):
                case (CheckResult.LOW):
                    // "本件追加担保・保証時価額は0から9,999,999までの範囲値で入力してください。"
                    SbrErrItem.Append(GetErrorRangeMessage(strItemName, "0", "9,999,999", MessageId_Approval.ERIN5008));
                    blResult = false;
                    break;
                case (CheckResult.NORMAL):
                    blCheckGuaranteeJika = true;
                    break;
                default:
                    break;
            }

            // 既存担保・保証時価余力額
            strItemName = "既存担保・保証時価余力額";
            bool blCheckGuaranteeYoryoku = false;
            switch (CheckValue.CheckDecimalRange(0, tbxGuaranteeYoryoku.Text, 9999999m))
            {
                case (CheckResult.NULL):
                case (CheckResult.BLANK):
                    // {0}は必須入力です。
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                    break;
                case (CheckResult.ERROR):
                    // "{0}は半角数字で入力してください。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                    blResult = false;
                    break;
                case (CheckResult.HIGH):
                case (CheckResult.LOW):
                    // "既存担保・保証時価余力額は0から9,999,999までの範囲値で入力してください。"
                    SbrErrItem.Append(GetErrorRangeMessage(strItemName, "0", "9,999,999", MessageId_Approval.ERIN5008));
                    blResult = false;
                    break;
                case (CheckResult.NORMAL):
                    blCheckGuaranteeYoryoku = true;
                    break;
                default:
                    break;
            }

            // 申請金利
            strItemName = "申請金利";
            switch (CheckValue.CheckDecimalRange(0.001m, tbxInterestRate.Text, 99.999m))
            {
                case (CheckResult.NULL):
                case (CheckResult.BLANK):
                    // {0}は必須入力です。
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5010));
                    blResult = false;
                    break;
                case (CheckResult.ERROR):
                    // "{0}は半角数字で入力してください。"
                    SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                    blResult = false;
                    break;
                case (CheckResult.HIGH):
                case (CheckResult.LOW):
                    // "申請金利は0.001から99.999までの範囲値で入力してください。"
                    SbrErrItem.Append(GetErrorRangeMessage(strItemName, "0.001", "99.999", MessageId_Approval.ERIN5008));
                    blResult = false;
                    break;
                default:
                    break;
            }

            // 固定金利期間
            strItemName = "固定金利期間";
            // 固定金利の場合
            if (!ddlVariableInterestCode.SelectedValue.Equals(R_KINRINENGEN1))
            {
                switch (CheckValue.CheckIntRange(1, tbxFixedIntstRatePeriod.Text, 999))
                {
                    case (CheckResult.NULL):
                    case (CheckResult.BLANK):
                        // {0}は必須入力です。
                        SbrErrItem.Append(GetErrorMessage("固定金利の場合、" + strItemName, MessageId_Approval.ERIN5010));
                        blResult = false;
                        break;
                    case (CheckResult.ERROR):
                        // "{0}は半角数字で入力してください。"
                        SbrErrItem.Append(GetErrorMessage(strItemName, MessageId_Approval.ERIN5006));
                        blResult = false;
                        break;
                    case (CheckResult.HIGH):
                    case (CheckResult.LOW):
                        // "固定金利期間は1から999までの範囲値で入力してください。"
                        SbrErrItem.Append(GetErrorRangeMessage(strItemName, "1", "999", MessageId_Approval.ERIN5008));
                        blResult = false;
                        break;
                    default:
                        break;
                }
            }
            // 変動金利の場合
            else
            {
                if (!Util.IsEmpty(tbxFixedIntstRatePeriod.Text))
                {
                    // "変動金利の場合、固定金利期間は入力不要です。"
                    SbrErrItem.Append(GetErrorMessage("変動金利の場合、" + strItemName, MessageId_Approval.ERIN5213));
                    blResult = false;
                }
            }

            // 本件追加担保・保証時価額が申請金額を超えている場合
            if (blCheckGuaranteeJika && blCheckExecScheduledMoney)
            {
                if (Util.Str2Decimal(tbxGuaranteeJika.Text) > Util.Str2Decimal(tbxExecScheduledMoney.Text))
                {
                    // "本件追加担保・保証時価額が申請金額を超えています。"
                    string strMsg = Util.GetMessage(messageManager,
                        new string[] { "text1", "text2" },
                        new string[] { "本件追加担保・保証時価額", "申請金額" },
                        MessageId_Approval.ERIN5214);
                    SbrErrItem.Append(strMsg + "<br>");
                    blResult = false;
                }
            }

            // 既存担保・保証時価余力額が（申請金額－本件追加担保・保証時価額）を超えている場合
            if (blCheckGuaranteeYoryoku && blCheckGuaranteeJika && blCheckExecScheduledMoney)
            {
                if (Util.Str2Decimal(tbxGuaranteeYoryoku.Text) > Util.Str2Decimal(tbxExecScheduledMoney.Text) - Util.Str2Decimal(tbxGuaranteeJika.Text))
                {
                    // "既存担保・保証時価余力額が（申請金額－本件追加担保・保証時価額）を超えています。"
                    string strMsg = Util.GetMessage(messageManager,
                        new string[] { "text1", "text2" },
                        new string[] { "既存担保・保証時価余力額", "（申請金額－本件追加担保・保証時価額）" },
                        MessageId_Approval.ERIN5214);
                    SbrErrItem.Append(strMsg + "<br>");
                    blResult = false;
                }
            }
            return blResult;
        }
        #endregion

        #region メッセージ作成処理
        /// <summary>
        /// エラーメッセージを作成する。
        /// </summary>
        /// <param name="strItem">エラー対象項目</param>
        /// <param name="strMsgId">エラーメッセージ番号</param>
        /// <returns>エラーメッセージ</returns>
        /// <remarks>
        /// エラーメッセージを作成し、リターンする。
        /// </remarks>
        protected string GetErrorMessage(string strItem, string strMsgId)
        {
            // メッセージのリターン
            return Util.GetMessage(messageManager, strItem, strMsgId) + "<br>";
        }

        /// <summary>
        /// 範囲チェック項目のエラーメッセージを作成する。
        /// </summary>
        /// <param name="strItem">エラー対象項目</param>
        /// <param name="strMin">入力できる最小値</param>
        /// <param name="strMax">入力できる最大値</param>
        /// <param name="strMsgId">エラーメッセージＩＤ</param>
        /// <returns>エラーメッセージ</returns>
        /// <remarks>
        /// 範囲チェック項目のエラーメッセージを作成し、リターンする。
        /// </remarks>
        protected string GetErrorRangeMessage(string strItem, string strMin, string strMax, string strMsgId)
        {
            // メッセージの設定
            string[] strMsgTitle = new string[3] { "text", "min", "max" };
            string[] strMsgContent = new string[3] { strItem, strMin, strMax };

            // メッセージの作成
            string strMsg = Util.GetMessage(messageManager, strMsgTitle, strMsgContent, strMsgId);

            // メッセージのリターン
            return strMsg + "<br>";
        }
        #endregion

        #region 登録ボタン処理
        /// <summary>
        /// 登録ボタン押下時の処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生したオブジェクト</param>
        /// <param name="e">イベントデータを持つ個体クラス</param>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>多重サブミットチェック。</item>
        /// <item>入力データの有効性チェックを行う。
        /// <para>－チェックエラーの場合は、エラーメッセージを表示する。</para>
        /// </item>
        /// <item>『適正金利検証情報』テーブルへの登録を行う。</item>
        /// <para>－例外エラーメッセージを画面へ出力する。</para>
        /// <para>－表示状態を"READ"に切り替える。</para>
        /// </list>
        /// </remarks>
        protected void btnRegist_Click(object sender, System.EventArgs e)
        {
            // 多重サブミットチェック
            if (this.IsReRequest)
            {
                return;
            }

            // チェック処理
            if (!this.RegistCheck())
            {
                return;
            }

            // 登録処理
            try
            {
                ApprovalKinriVerificationRegistParameter p =
                    (ApprovalKinriVerificationRegistParameter)this.CreateParameter("W090_002");
                using (ILogic logic = (ILogic)this.CreateLogic("W090_002"))
                {
                    if (!logic.Execute(p))
                    {
                        // エラーあり
                        this.AppendMessage(p.Messages);

                        return;
                    }

                    if (this.IsUpdate)
                    {
                        this.AppendMessage(MessageId_Approval.IRIN5011, "適正金利検証");
                    }
                    else
                    {
                        this.AppendMessage(MessageId_Approval.IRIN5010, "適正金利検証");
                    }
                }
            }
            catch (LogicException ex)
            {
                // 業務プロセスエラー
                this.AppendMessage(Isid.RiskTaker.Common.Constant.MessageAreaLevel.BusinessError, ex.Message);
                this.SetupControlState("READ");
            }
        }
        #endregion

        #region DECIMAL型数字を文字列に変換する
        /// <summary>
        /// DECIMAL型数字を文字列に変換する。
        /// </summary>
        /// <param name="deNum">Decimal値</param>
        /// <param name="roundPos">有効小数桁数</param>
        /// <returns>切り捨て処理後の数値</returns>
        private string Dec2Str(decimal deNum, int roundPos)
        {
            return Util.Num2Str(deNum, roundPos);
        }
        #endregion
    }
}