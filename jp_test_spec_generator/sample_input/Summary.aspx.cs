
using Isid.Copera.Exception;
using Isid.Copera.Util.Check;
using Isid.Copera.Util.Message;
using Isid.Copera.Web.UI;
using Isid.RiskTaker.Common;
using Isid.RiskTaker.Common.Access;
using Isid.RiskTaker.Common.Ado;
using Isid.RiskTaker.Common.BusinessLogic;
using Isid.RiskTaker.Common.ExceptionClass;
using Isid.RiskTaker.Common.Info;
using Isid.RiskTaker.Common.Message;
using Isid.RiskTaker.Common.SessionInfo;
using Isid.RiskTaker.Common.UI;
using Isid.RiskTaker.Common.Utility;

using Isid.RiskTaker.Customer.Common.SessionInfo;
using Isid.RiskTaker.Portal.Common.Utility;
using Isid.RiskTaker.Web;
using log4net;
using System;
using System.Collections;
using System.Data;
using System.Data.SqlClient;
using System.Data.SqlTypes;
using System.Drawing;
using System.IO;
using System.Runtime.CompilerServices;
using System.Runtime.Remoting.Contexts;
using System.Security.Cryptography;
using System.Text;
using System.Web;
using System.Web.UI;
using System.Web.UI.HtmlControls;
using System.Web.UI.WebControls;
using System.Xml;
using System.Xml.Linq;


namespace Isid.RiskTaker.Web
{
    public partial class Summary : Isid.RiskTaker.Common.UI.DPage
    {
        #region プロプティを定義する

        /// <summary>
        /// メッセージを取得する。
        /// </summary>
        private static readonly IMessageManager messageManager =
            Common.Message.MessageManager.GetInstance(MessageId_Recovery.CATEGORY);

        /// <summary>
        /// ログ情報を取得する。
        /// </summary>
        private static readonly ILog log = LogManager.GetLogger(typeof(Summary));

        /// <summary>
        /// クラスメンバー変数：セッション情報
        /// </summary>
        protected Isid.RiskTaker.Common.SessionInfo.Session session = null;

        /// <summary>
        /// メッセージエリア管理オブジェクト
        /// </summary>	
        private WebMessageArea webMessage;

        /// <summary>
        /// クラスメンバー変数：入力チェックのエラーメッセージを設定する。
        /// </summary>
        private StringBuilder StbLogMsg;

        /// <summary>
        /// 帳票名称定義ファイル.RootNode
        /// </summary>
        private static XmlElement xmlRootNode = null;

        /// <summary>
        /// 帳票名称定義ファイル.NameSpace_Node
        /// </summary>
        private static XmlElement xmlNodeNS = null;

        /// <summary>
        /// 帳票名称定義ファイル.AssemblyName_Node
        /// </summary>
        private static XmlElement xmlNodeAL = null;

        /// <summary>
        /// 帳票XMLファイル名
        /// </summary>
        private const string XML_FILE_NAME = "PrintCustomerReport.xml";

        /// <summary>
        /// 帳票ノード一覧（Sort済み）
        /// </summary>
        private static ArrayList arlItems = new ArrayList();

        /// <summary>
        /// 名前空間
        /// </summary>
        private static string strNameSpace = string.Empty;

        /// <summary>
        /// アセンブリ名
        /// </summary>
        private static string strAssemblyName = string.Empty;

        /// <summary>
        /// 店番
        /// </summary>
        protected string BranchNo
        {
            get
            {
                return ViewState["BranchNo"] as string;
            }

            set
            {
                ViewState["BranchNo"] = value;
            }
        }

        /// <summary>
        /// 顧客番号
        /// </summary>
        protected string CustomerNo
        {
            get
            {
                return ViewState["CustomerNo"] as string;
            }
            set
            {
                ViewState["CustomerNo"] = value;
            }
        }

        /// <summary>
        /// 参照モード判定
        /// </summary>
        protected bool IsReferenceMode
        {
            get
            {
                string strMode = Util.Null2Str(Request.QueryString["DisplayMode"]);
                return strMode.Equals("1", StringComparison.OrdinalIgnoreCase);
            }
        }

        #endregion

        #region 定数値

        /// <summary>
        /// 営業店の部店格
        /// </summary>
        //protected readonly string STR_BUTENKAKU = "BUTENKAKU1";

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
        /// <returns>なし</returns>
        private void InitializeComponent()
        {
        }

        #endregion

        /// <summary>
        /// ページロード処理を行う。
        /// </summary>
        /// <param name="sender">イベントが発生されたオブジェクト</param>
        /// <param name="e">イベントデー
        protected void Page_Load(object sender, EventArgs e)
        {
            try
            {
                string strMsg = "";

                // ページ遷移チェック
                MenuManager.CheckCorrectTransfer(this);

                webMessage = new WebMessageArea(messageBox);

                // セッションの情報を取得する。
                session = Isid.RiskTaker.Common.SessionInfo.Session.GetSession(this);
                if (session == null)
                {
                    // セッションがタイムアウトされた場合、例外スロー
                    strMsg = messageManager.GetMessage(MessageId_Recovery.EREC0000);
                    throw new SessionTimeoutException(strMsg);
                }

                if (session.GroupListAll == null || session.GroupListAll.Length < 1)
                {
                    strMsg = Util.GetMessage(messageManager, "ユーザレベル", MessageId_Recovery.EREC0001);
                    throw new DArgumentException(strMsg);
                }

                //userRoleId = GetUserRoleId();

                if (!IsPostBack)
                {
                    string strBranchNo = Util.Null2Str(Request.QueryString["BranchNo"]);
                    string strCustomerNo = Util.Null2Str(Request.QueryString["CustomerNo"]);
                    this.hidReferenceMode.Value = this.IsReferenceMode ? "1" : "0";
                    // 店番
                    if (Util.IsEmpty(session.User_Buten))
                    {
                        strMsg = Util.GetMessage(messageManager, "店番", MessageId_Recovery.EREC0001);
                        throw new DArgumentException(strMsg);
                    }

                    // 店名
                    if (Util.IsEmpty(session.User_ButenMei))
                    {
                        strMsg = Util.GetMessage(messageManager, "店名", MessageId_Recovery.EREC0001);
                        throw new DArgumentException(strMsg);
                    }

                    // 顧客番号
                    if (!Util.IsEmpty(strCustomerNo))
                    {
                        this.tbxCustomerNo.Text = strCustomerNo;
                    }
                    else if (!Util.IsEmpty(session.Customer_ID))
                    {
                        this.tbxCustomerNo.Text = session.Customer_ID;
                    }

                    // 顧客名
                    if (!Util.IsEmpty(session.Customer_Name))
                    {
                        //this.lblCustomerName = session.Customer_Name;
                    }

                    // 店番初期設定
                    this.InitializeBranchDropDown(strBranchNo);

                    // ユーザ区分に応じた店番活性制御
                    this.ApplyBranchControlByUserRole();

                    // 事象ステータス
                    this.LoadJisyoStatus();

                    // 参照モード時はQueryStringの店番・顧客番号を優先して画面表示／検索を行う
                    if (this.IsReferenceMode)
                    {
                        if (!Util.IsEmpty(strBranchNo) && ddlBranchNo.Items.FindByValue(strBranchNo) != null)
                        {
                            this.ddlBranchNo.SelectedValue = strBranchNo;
                        }

                        if (!Util.IsEmpty(strCustomerNo))
                        {
                            this.tbxCustomerNo.Text = strCustomerNo;
                        }
                    }

                    // 帳票設定初期化
                    InitReportNameInfo();

                    // 画面の表示処理を行います
                    this.Display();

                    // 参照モード設定
                    if (this.IsReferenceMode)
                    {
                        this.SetReferenceMode();
                    }
                }
            }
            //当メッソドでThrowした例外
            catch (SessionTimeoutException ex)
            {
                // エラーログ作成
                StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: Page_Load");
                StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                StbLogMsg.Append("\r\n  e     : " + e.ToString());
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            //当メッソドでThrowした例外
            catch (DArgumentException ex)
            {
                // エラーログ作成
                StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: Page_Load");
                StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                StbLogMsg.Append("\r\n  e     : " + e.ToString());
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (DApplicationException ex)
            {
                // エラーログ作成
                StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: Page_Load");
                StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                StbLogMsg.Append("\r\n  e     : " + e.ToString());
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                // エラログ出力
                StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: Page_Load");
                StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                StbLogMsg.Append("\r\n  e     : " + e.ToString());
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());

                //システムエラーページを表示する場合（エラーページへ自動的に移動する）
                throw new UnknownException(ex.Message, ex);
            }

        }

        /// <summary>
        /// 事象ステータスを取得し、RadioButtonListへバインドする。
        /// </summary>
        private void LoadJisyoStatus()
        {
            SqlConnection sqlCon = null;

            try
            {
                // ▼ ストアドプロシージャ生成
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_sel04", ref sqlCon);

                // ▼ パラメータ設定（コードキー：事象ステータス）
                SPFactory.SetSPCharParam(cmd, "@CodeKey", "JISYOSTUTAS", 20, false);

                // ▼ SP実行し、データ取得
                DataSet ds = SPFactory.ExecuteSPDataSet(cmd);
                DataTable dt = ds.Tables[0];

                // ▼ RadioButtonListへデータバインド
                rblJisyoStatus.DataSource = dt;

                // 表示項目（名称）
                rblJisyoStatus.DataTextField = "CChny_HanyouCodeNaiyou";

                // 値項目（コード値）
                rblJisyoStatus.DataValueField = "CChny_HanyouUniqueKey";

                rblJisyoStatus.DataBind();

                // ▼ 初期状態：未選択
                rblJisyoStatus.ClearSelection();
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: LoadJisyoStatus");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: LoadJisyoStatus");
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw new UnknownException(ex.Message, ex);
            }
            finally
            {
                // ▼ コネクション解放
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }

        /// <summary>
        /// 参照モード時の画面制御を行う。
        /// </summary>
        private void SetReferenceMode()
        {
            this.ddlBranchNo.Enabled = false;
            this.tbxCustomerNo.ReadOnly = true;
            this.btnCustShow.Enabled = false;
            this.rblJisyoStatus.Enabled = false;

            this.txtReason.ReadOnly = true;
            this.txtCurrentSituation.ReadOnly = true;
            this.txtPolicy.ReadOnly = true;
            this.txtRemarks.ReadOnly = true;

            this.btnRegister.Enabled = false;
            // this.Dummy.Enabled = false;
        }

        /// <summary>
        /// ユーザ区分に応じて店番・店名の活性状態を設定する。
        /// 本部ユーザのみ活性とする。
        /// </summary>
        private void ApplyBranchControlByUserRole()
        {
            // 本部ユーザ以外は非活性
            if (session.IsEigyou)
            {
                this.ddlBranchNo.Enabled = false;

                // 非本部ユーザは自店固定
                if (this.ddlBranchNo.Items.FindByValue(session.User_Buten) != null)
                {
                    this.ddlBranchNo.SelectedValue = session.User_Buten;
                    this.BranchNo = this.GetSelectedBranchNo();
                }
            }
            else
            {
                // 本部ユーザのみ活性
                this.ddlBranchNo.Enabled = true;
            }
        }

        /// <summary>
        /// 店番ドロップダウンを初期設定する。
        /// </summary>
        /// <param name="branchNo">選択対象の店番</param>
        private void InitializeBranchDropDown(string branchNo)
        {
            string targetBranchNo = Util.IsEmpty(branchNo) ? session.User_Buten : branchNo;

            ddlBranchNo.Items.Clear();
            Buten.AttachDropDownList(ddlBranchNo, session.User_ButenKaku, targetBranchNo, false, true, null);

            if (ddlBranchNo.Items.Count > 0 && string.Empty.Equals(ddlBranchNo.Items[0].Value))
            {
                ddlBranchNo.Items.RemoveAt(0);
            }

            // 参照モードでQueryStringの店番が一覧にない場合も表示できるように追加
            if (this.IsReferenceMode && !Util.IsEmpty(branchNo) && ddlBranchNo.Items.FindByValue(branchNo) == null)
            {
                ddlBranchNo.Items.Add(new ListItem(branchNo, branchNo));
            }

            // QueryStringで店番が渡された場合はそれを優先
            if (!Util.IsEmpty(branchNo) && ddlBranchNo.Items.FindByValue(branchNo) != null)
            {
                ddlBranchNo.SelectedValue = branchNo;
            }
            else if (ddlBranchNo.Items.FindByValue(session.User_Buten) != null)
            {
                ddlBranchNo.SelectedValue = session.User_Buten;
            }
            else if (ddlBranchNo.Items.Count > 0)
            {
                ddlBranchNo.SelectedIndex = 0;
            }

            this.BranchNo = this.GetSelectedBranchNo();
        }

        /// <summary>
        /// 現在選択中の店番を取得する。
        /// </summary>
        /// <returns>店番</returns>
        private string GetSelectedBranchNo()
        {
            if (this.ddlBranchNo == null || this.ddlBranchNo.Items.Count == 0)
            {
                return string.Empty;
            }

            if (this.ddlBranchNo.SelectedItem != null)
            {
                return this.ddlBranchNo.SelectedItem.Value.Trim();
            }

            return Util.Null2Str(this.ddlBranchNo.SelectedValue).Trim();
        }

        /// <summary>
        /// 店番変更時の処理を行う。
        /// </summary>
        protected void ddlBranchNo_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (this.IsReferenceMode)
            {
                return;
            }

            // 非本部ユーザは自店固定
            if (session.IsEigyou)
            {
                if (this.ddlBranchNo.Items.FindByValue(session.User_Buten) != null)
                {
                    this.ddlBranchNo.SelectedValue = session.User_Buten;
                }

                this.BranchNo = this.GetSelectedBranchNo();
                return;
            }

            // 顧客情報クリア
            this.tbxCustomerNo.Text = string.Empty;
            this.lblCustomerName.Text = string.Empty;

            // 検索条件保持用ViewStateクリア
            this.CustomerNo = string.Empty;
            this.BranchNo = this.GetSelectedBranchNo();

            // 一覧・概況項目クリア
            this.ClearDisplayArea();
        }

        /// <summary>
        /// 一覧・概況表示エリアをクリアする。
        /// </summary>
        private void ClearDisplayArea()
        {
            // 債権明細一覧クリア
            this.rptSaikenMeisai.DataSource = null;
            this.rptSaikenMeisai.DataBind();

            // 延滞・悪化事象一覧クリア
            this.rptJishoList.DataSource = null;
            this.rptJishoList.DataBind();

            // 最終更新情報クリア
            this.lblUpdateDate.Text = string.Empty;
            this.lblUpdateUser.Text = string.Empty;

            // 顧客コメントクリア
            this.txtReason.Text = string.Empty;
            this.txtCurrentSituation.Text = string.Empty;
            this.txtPolicy.Text = string.Empty;
            this.txtRemarks.Text = string.Empty;

            // 事象ステータス・排他制御情報クリア
            this.rblJisyoStatus.ClearSelection();
            this.hidUpdateDateTime.Value = string.Empty;
        }

        #region 表示処理
        /// <summary>
        /// DBよりデータを取得して画面に表示する。
        /// </summary>
        /// <returns>なし</returns>
        /// <remarks>
        /// <list type="number">
        /// <item>クラスを使用してDBよりデータを取得する。</item>
        /// <item>コントロールへデータを設定する。</item>
        /// <item>一覧コントロールへデータを設定する。</item>
        /// </list>
        /// </remarks>
        private void Display()
        {
            BranchNo = this.GetSelectedBranchNo();
            CustomerNo = this.tbxCustomerNo.Text.Trim();

            // 債権明細一覧表示
            DisplaySaikenMeisaiList();

            // 延滞・悪化事象一覧
            DisplayJishoList();

            // 顧客コメント
            DisplayComment();

        }
        #endregion

        #region 債権明細一覧表示
        /// <summary>
        /// 債権明細一覧を取得し画面へ表示する。（SP直接呼び出し）
        /// </summary>
        private void DisplaySaikenMeisaiList()
        {
            SqlConnection sqlCon = null;

            try
            {
                // ▼ SP呼び出し
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_sel01", ref sqlCon);

                // ▼ パラメータ設定
                SPFactory.SetSPCharParam(cmd, "@BranchNo", this.BranchNo, 4, blOutput: false);
                SPFactory.SetSPCharParam(cmd, "@CustomerNo", this.CustomerNo, 12, blOutput: false);

                // ▼ 実行
                DataSet ds = SPFactory.ExecuteSPDataSet(cmd);

                // ▼ データ取得
                DataTable dt = ds.Tables[0];

                // ▼ 画面反映
                this.rptSaikenMeisai.DataSource = dt;
                this.rptSaikenMeisai.DataBind();
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplaySaikenMeisaiList");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplaySaikenMeisaiList");
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw new UnknownException(ex.Message, ex);
            }
            finally
            {
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }
        #endregion

        #region 延滞・悪化事象一覧表示
        private void DisplayJishoList()
        {
            SqlConnection sqlCon = null;

            try
            {
                // ▼ SP呼び出し
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_sel02", ref sqlCon);

                // ▼ パラメータ
                SPFactory.SetSPCharParam(cmd, "@BranchNo", this.BranchNo, 4, false);
                SPFactory.SetSPCharParam(cmd, "@CustomerNo", this.CustomerNo, 12, false);

                // ▼ 実行
                DataSet ds = SPFactory.ExecuteSPDataSet(cmd);
                DataTable dt = ds.Tables[0];

                // ▼ 画面反映
                this.rptJishoList.DataSource = dt;
                this.rptJishoList.DataBind();
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplayJishoList");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplayJishoList");
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw new UnknownException(ex.Message, ex);
            }
            finally
            {
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }
        #endregion

        #region 顧客コメント
        private void DisplayComment()
        {
            SqlConnection sqlCon = null;

            try
            {
                // ▼ SP呼び出し
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_sel03", ref sqlCon);

                // ▼ パラメータ
                SPFactory.SetSPCharParam(cmd, "@BranchNo", this.BranchNo, 4, false);
                SPFactory.SetSPCharParam(cmd, "@CustomerNo", this.CustomerNo, 12, false);

                // ▼ 実行
                DataSet ds = SPFactory.ExecuteSPDataSet(cmd);
                DataTable dt = ds.Tables[0];

                // ▼ データ存在チェック
                if (dt.Rows.Count > 0)
                {
                    DataRow row = dt.Rows[0];

                    // ▼ 最終更新情報
                    this.lblUpdateDate.Text = row["UpdateDate"].ToString();
                    this.lblUpdateUser.Text = row["UpdateUser"].ToString();

                    // ▼ コメント情報
                    this.txtReason.Text = row["Reason"].ToString();
                    this.txtCurrentSituation.Text = row["CurrentSituation"].ToString();
                    this.txtPolicy.Text = row["Policy"].ToString();
                    this.txtRemarks.Text = row["Remarks"].ToString();

                    // ▼ 事象ステータス設定（RadioButtonList）
                    string status = row["Status"] == DBNull.Value ? "" : row["Status"].ToString();

                    if (!string.IsNullOrEmpty(status))
                    {
                        // ▼ 該当する値を選択状態にする
                        if (rblJisyoStatus.Items.FindByValue(status) != null)
                        {
                            rblJisyoStatus.SelectedValue = status;
                        }
                    }
                    else
                    {
                        // ▼ ステータス未設定の場合は未選択
                        rblJisyoStatus.ClearSelection();
                    }

                    // ▼ 排他チェック用（更新日時保持）
                    if (dt.Columns.Contains("UpdateDateTimeRaw") && row["UpdateDateTimeRaw"] != DBNull.Value)
                    {
                        this.hidUpdateDateTime.Value = row["UpdateDateTimeRaw"].ToString();
                    }
                    else
                    {
                        this.hidUpdateDateTime.Value = string.Empty;
                    }
                }
                else
                {
                    // ▼ 最終更新情報
                    this.lblUpdateDate.Text = string.Empty;
                    this.lblUpdateUser.Text = string.Empty;

                    // ▼ コメント情報
                    this.txtReason.Text = string.Empty;
                    this.txtCurrentSituation.Text = string.Empty;
                    this.txtPolicy.Text = string.Empty;
                    this.txtRemarks.Text = string.Empty;

                    // ▼ 事象ステータス設定（RadioButtonList）未選択
                    rblJisyoStatus.ClearSelection();

                    // ▼ 排他チェック用（データなし時はクリア）
                    this.hidUpdateDateTime.Value = string.Empty;
                }
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplayComment");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: DisplayComment");
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw new UnknownException(ex.Message, ex);
            }
            finally
            {
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }
        #endregion

        /// <summary>
        /// char(8)日付（yyyyMMdd）→ yyyy/MM/dd 変換
        /// </summary>
        protected string FormatDate8(object value)
        {
            if (value == null || value == DBNull.Value) return "";

            string str = value.ToString().Trim();

            if (str.Length != 8) return str;

            return $"{str.Substring(0, 4)}/{str.Substring(4, 2)}/{str.Substring(6, 2)}";
        }

        /// <summary>
        /// 金額を千円単位で表示（切り捨て）
        /// </summary>
        /// <param name="value">表示する金額</param>
        /// <returns>千円単位の金額</returns>
        protected string FormatZandaka(object value)
        {
            if (value == DBNull.Value || value == null)
            {
                return "0";
            }

            decimal amount = Convert.ToDecimal(value);

            // 千円単位 + 切り捨て
            decimal result = Math.Floor(amount / 1000);

            return string.Format("{0:N0}", result);
        }

        protected void btnCustShow_Click(object sender, EventArgs e)
        {
            // 多重サブミットチェック
            if (IsReRequest)
            {
                return;
            }
            // 参照モードチェック
            if (this.IsReferenceMode)
            {
                return;
            }

            // 顧客名（略称）の表示
            string strBranchNo = this.GetSelectedBranchNo();
            string strCustomerNo = this.tbxCustomerNo.Text.Trim();
            if ((!string.IsNullOrEmpty(strBranchNo)) && (!string.IsNullOrEmpty(strCustomerNo)))
            {
                string strCusotmerName = CustomerName.GetCustomerName(strBranchNo, strCustomerNo);
                lblCustomerName.Text = strCusotmerName;
                if (string.IsNullOrEmpty(strCusotmerName))
                {
                    // エラーメッセージ表示：顧客情報が存在しません。
                    string[] strTitle = new string[] { "branch", "custID" };
                    string[] strContent = new string[] { strBranchNo, strCustomerNo };

                    // 店番(XXXX)、顧客番号(YYYYYYYY)は存在しません。
                    string errMsg = Util.GetMessage(messageManager, strTitle, strContent, MessageId_Recovery.EREC0002);
                    //メッセージの出力
                    messageBox.PrintError(errMsg);
                    // ログ出力
                    StbLogMsg = new StringBuilder();
                    StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + errMsg));
                    StbLogMsg.Append("\r\nErrorMethod: btnCustShow_Click");
                    StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                    StbLogMsg.Append("\r\n  e     : " + e.ToString());
                    log.Error(StbLogMsg.ToString());
                }
            }

            // 画面の表示処理を行います
            this.Display();
        }

        protected void btnRegister_Click(object sender, EventArgs e)
        {
            if (this.IsReferenceMode)
            {
                return;
            }

            SqlConnection sqlCon = null;
            try
            {
                // ▼ 入力チェック（文字数チェック）
                StringBuilder strErrMsg = new StringBuilder();
                if (!RegisterCheck(strErrMsg))
                {
                    messageBox.PrintError(strErrMsg.ToString());
                    return;
                }
                // ▼ SP呼び出し
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_upd01", ref sqlCon);

                this.BranchNo = this.GetSelectedBranchNo();
                // ▼ パラメータ設定
                SPFactory.SetSPCharParam(cmd, "@BranchNo", this.BranchNo, 4, false);
                SPFactory.SetSPCharParam(cmd, "@CustomerNo", this.CustomerNo, 12, false);

                SPFactory.SetSPCharParam(cmd, "@Status", rblJisyoStatus.SelectedValue, 15, false);
                SPFactory.SetSPVarCharParam(cmd, "@Reason", this.txtReason.Text, 1000, false);
                SPFactory.SetSPVarCharParam(cmd, "@CurrentSituation", this.txtCurrentSituation.Text, 1000, false);
                SPFactory.SetSPVarCharParam(cmd, "@Policy", this.txtPolicy.Text, 1000, false);
                SPFactory.SetSPVarCharParam(cmd, "@Remarks", this.txtRemarks.Text, 1000, false);

                // ▼ 更新者（セッションから取得）
                // セッション取得
                session = Isid.RiskTaker.Common.SessionInfo.Session.GetSession(this);
                SPFactory.SetSPCharParam(cmd, "@UpdateUserNo", session.User_ID, 12, false);

                // ▼ 排他チェック用（hiddenから取得）
                if (!string.IsNullOrEmpty(this.hidUpdateDateTime.Value))
                {
                    SPFactory.SetSPVarCharParam(cmd, "@OldUpdateDateTime", this.hidUpdateDateTime.Value, 23, false);
                }
                //else
                //{
                //    SPFactory.SetSPDatetimeParam(cmd, "@OldUpdateDateTime", DBNull.Value, false);
                //}

                // ▼ 戻り値パラメータ
                SqlParameter resultParam = new SqlParameter("@Result", SqlDbType.Int);
                resultParam.Direction = ParameterDirection.Output;
                cmd.Parameters.Add(resultParam);

                // ▼ 実行
                SPFactory.ExecuteSPNonQuery(cmd);

                int result = (resultParam.Value == DBNull.Value) ? 0 : Convert.ToInt32(resultParam.Value);

                // ▼ 結果判定
                if (result == -1)
                {
                    // ▼ 排他エラー
                    //    "ECOM0059: 概況は既に更新されていますので、更新できません。"

                    // エラーメッセージの設定
                    string strText = "概況";
                    // {text}は既に更新されていますので、更新できません。
                    string errMsg = Util.GetMessage(messageManager, strText, MessageId_Recovery.EREC0008);
                    //メッセージの出力
                    messageBox.PrintError(errMsg);
                    // ログ出力
                    StbLogMsg = new StringBuilder();
                    StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + errMsg));
                    StbLogMsg.Append("\r\nErrorMethod: btnUpdate_ServerClick");
                    StbLogMsg.Append("\r\n  sender: " + sender.ToString());
                    StbLogMsg.Append("\r\n  e     : " + e.ToString());
                    log.Error(StbLogMsg.ToString());

                    //blCheck = false;
                    return;
                }

                // ▼ 正常終了メッセージ
                //this.AppendMessage(
                //    Isid.RiskTaker.Common.Constant.MessageAreaLevel.Info,
                //    "更新が完了しました。"
                //);

                // ▼ 再表示（最新データ取得）
                this.Display();
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: btnRegister_Click");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                // ▼ システムエラー
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: btnRegister_Click");
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());

                throw;
            }
            finally
            {
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }

        /// <summary>
        /// 登録時入力チェックを行う。
        /// </summary>
        /// <param name="strErrMsg">エラーメッセージ</param>
        /// <returns>true:正常、false:エラー</returns>
        private bool RegisterCheck(StringBuilder strErrMsg)
        {
            bool blCheck = true;

            if (CheckValue.CheckStringRange(this.txtReason.Text, 2000) == CheckResult.HIGH)
            {
                strErrMsg.Append(GetStrErrorMessage("事故及び延滞に至った原因", "1000", MessageId_Recovery.EREC0006) + "<br>");
                blCheck = false;
            }

            if (CheckValue.CheckStringRange(this.txtCurrentSituation.Text, 2000) == CheckResult.HIGH)
            {
                strErrMsg.Append(GetStrErrorMessage("債務者および保証人の現況", "1000", MessageId_Recovery.EREC0006) + "<br>");
                blCheck = false;
            }

            if (CheckValue.CheckStringRange(this.txtPolicy.Text, 2000) == CheckResult.HIGH)
            {
                strErrMsg.Append(GetStrErrorMessage("回収、解消の方針、スケジュール", "1000", MessageId_Recovery.EREC0006) + "<br>");
                blCheck = false;
            }

            if (CheckValue.CheckStringRange(this.txtRemarks.Text, 2000) == CheckResult.HIGH)
            {
                strErrMsg.Append(GetStrErrorMessage("備考、特記事項", "1000", MessageId_Recovery.EREC0006) + "<br>");
                blCheck = false;
            }

            return blCheck;
        }

        /// <summary>
        /// 文字入力項目のチェック時のエラーメッセージを作成する。
        /// </summary>
        /// <param name="_strItem">エラー対象項目</param>
        /// <param name="_strLen">桁数</param>
        /// <param name="_strMsgNo">エラーメッセージ番号</param>
        /// <returns>エラーメッセージ</returns>
        private string GetStrErrorMessage(string _strItem, string _strLen, string _strMsgNo)
        {
            string[] strMsgTitle = new string[2] { "text", "Size" };
            string[] strMsgContent = new string[2] { _strItem, _strLen };

            return Util.GetMessage(messageManager, strMsgTitle, strMsgContent, _strMsgNo);
        }

        /// <summary>
        /// 債権明細一覧 イベント処理
        /// </summary>
        protected void rptSaikenMeisai_ItemCommand(object source, RepeaterCommandEventArgs e)
        {
            if (this.IsReferenceMode)
            {
                return;
            }

            // TODO：詳細画面へ遷移

        }

        /// <summary>
        /// 帳票設定XMLを読み込み、帳票情報を初期化する。
        /// </summary>
        private void InitReportNameInfo()
        {
            // ファイルのパス
            string strFilePath = Util.WebAppSetting(Constant.CONFIG_CONFIG_DIR) + Path.DirectorySeparatorChar + XML_FILE_NAME;
            FileInfo FIFilePath = new FileInfo(strFilePath);

            if (!FIFilePath.Exists)
            {
                throw new DApplicationException(Util.GetMessage(messageManager, "帳票定義ファイル", MessageId_Recovery.EREC0001));
            }

            XmlDocument xmlDoc = new XmlDocument();

            try
            {
                StringBuilder stbFilePath = new StringBuilder();

                // 定性要因情報項目ファイルをXmlDocumentとして取得
                xmlDoc.Load(strFilePath);
                // RootNode
                xmlRootNode = xmlDoc.DocumentElement;
                // 名前空間
                xmlNodeNS = (XmlElement)xmlRootNode.GetElementsByTagName("NameSpace")[0];
                strNameSpace = xmlNodeNS.InnerText;
                // アセンブル
                xmlNodeAL = (XmlElement)xmlRootNode.GetElementsByTagName("AssemblyName")[0];
                strAssemblyName = xmlNodeAL.InnerText;

                // 帳票名称を取得
                XmlNodeList xmlItemNodeList = xmlRootNode.GetElementsByTagName("ReportInfo");

                ArrayList arlNodes = new ArrayList();

                int intMin = int.MaxValue;
                int intMax = int.MinValue;
                XmlNode xmlTemp = null;
                for (int i = 0; i < xmlItemNodeList.Count; i++)
                {
                    foreach (XmlNode tmpNode in xmlItemNodeList)
                    {
                        int intTemp = Convert.ToInt32(GetSubElementText(tmpNode, "SortNo"));
                        if (intMin > intTemp && intMax < intTemp)
                        {
                            intMin = intTemp;
                            xmlTemp = tmpNode;
                        }
                    }
                    arlNodes.Add(xmlTemp);
                    intMax = intMin;
                    intMin = int.MaxValue;
                }

                if (arlNodes.Count < 1)
                {
                    // 登録されている帳票名称が存在しません。
                    throw new DApplicationException(Util.GetMessage(messageManager, "帳票名称", MessageId_Recovery.EREC0001));
                }

                // arlNodesをSortNoの昇順で並び替え
                arlItems = arlNodes;

                // ▼ 画面反映
                DataTable dtReport = CreateReportListDataTable();
                this.rptReportList.DataSource = dtReport;
                this.rptReportList.DataBind();

            }
            catch (Exception ex)
            {
                // 帳票名称の取得処理に失敗しました。
                throw new DApplicationException(Util.GetMessage(messageManager, "帳票名称の取得処理", MessageId_Recovery.EREC0001), ex);
            }
        }

        /// <summary>
        /// 帳票一覧データを作成する。
        /// </summary>
        /// <returns>帳票一覧DataTable</returns>
        private DataTable CreateReportListDataTable()
        {
            DataTable dtReport = new DataTable();
            dtReport.Columns.Add("ReportName");
            dtReport.Columns.Add("ReportClass");
            dtReport.Columns.Add("ElementId");
            dtReport.Columns.Add("Definition");
            dtReport.Columns.Add("Kind");

            foreach (XmlNode node in arlItems)
            {
                string strReportName = GetSubElementText(node, "ReportName");
                string strReportClass = GetSubElementText(node, "ReportClass");

                DataRow dr = dtReport.NewRow();
                dr["ReportName"] = strReportName;
                dr["ReportClass"] = strReportClass;

                // ▼ PWG_objectより帳票情報を取得
                SetReportObjectInfo(dr, strReportName);

                dtReport.Rows.Add(dr);
            }

            return dtReport;
        }

        /// <summary>
        /// PWG_objectより帳票オブジェクト情報を取得し、DataRowへ設定する。
        /// </summary>
        /// <param name="dr">設定対象DataRow</param>
        /// <param name="strReportName">帳票名</param>
        private void SetReportObjectInfo(DataRow dr, string strReportName)
        {
            SqlConnection sqlCon = null;

            try
            {
                // ▼ SP呼び出し（PWG_object取得用）
                SqlCommand cmd = SPFactory.CreateStoredProcedureCommand("spSummary_sel05", ref sqlCon);

                // ▼ パラメータ設定
                SPFactory.SetSPVarCharParam(cmd, "@FileName", strReportName, 255, false);
                SPFactory.SetSPCharParam(cmd, "@Kind", "RSHEET", 15, false);

                // ▼ 実行
                DataSet ds = SPFactory.ExecuteSPDataSet(cmd);
                DataTable dt = ds.Tables[0];

                if (dt.Rows.Count > 0)
                {
                    DataRow row = dt.Rows[0];
                    dr["ElementId"] = Util.Null2Str(row["WGobj_ElementId"]).Trim();
                    dr["Definition"] = Util.Null2Str(row["WGobj_Definition"]).Trim();
                    dr["Kind"] = Util.Null2Str(row["WGobj_Kind"]).Trim();
                }
                else
                {
                    dr["ElementId"] = string.Empty;
                    dr["Definition"] = string.Empty;
                    dr["Kind"] = "RSHEET";
                }
            }
            catch (DException dEx)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + dEx.Message));
                StbLogMsg.Append("\r\nErrorMethod: SetReportObjectInfo");
                StbLogMsg.Append("\r\nStack: \r\n" + dEx.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw;
            }
            catch (Exception ex)
            {
                StringBuilder StbLogMsg = new StringBuilder();
                StbLogMsg.Append(Util.GetLogMessage(this.Session, "\r\nErrorMessage: " + ex.Message));
                StbLogMsg.Append("\r\nErrorMethod: SetReportObjectInfo");
                StbLogMsg.Append("\r\n  ReportName: " + strReportName);
                StbLogMsg.Append("\r\nStack: \r\n" + ex.StackTrace);
                log.Error(StbLogMsg.ToString());
                throw new UnknownException(ex.Message, ex);
            }
            finally
            {
                SPFactory.DestroyStoredProcedure(sqlCon);
            }
        }

        /// <summary>
        /// XMLノードから指定したタグに該当するInnerTextを取得します。
        /// </summary>
        /// <param name="xmlNode">XMLのノード情報</param>
        /// <param name="strTagName">取得するタグ名</param>
        /// <returns>該当するInnerText文字列</returns>
        private static string GetSubElementText(XmlNode xmlNode, string strTagName)
        {
            try
            {
                return ((XmlElement)xmlNode).GetElementsByTagName(strTagName)[0].InnerText;
            }
            catch
            {
                return string.Empty;
            }
        }
    }
}