<%@ Import Namespace="Isid.RiskTaker.Common.Utility" %>

<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="Summary.aspx.cs" Inherits="Isid.RiskTaker.Web.Summary" %>

<%@ Register TagPrefix="cc1" Namespace="Isid.RiskTaker.Common.UI" Assembly="Isid.RiskTaker.Common" %>
<%--<%@ Register TagPrefix="cc2" Namespace="Isid.RiskTaker.debt_collection.Common.UI" Assembly="Isid.RiskTaker.debt_collection.Common" %>--%>

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head runat="server">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Summary</title>
    <link rel="stylesheet" href="../static/css/content.min.css" data-demo-href="./static/css/content.min.css" />
    <link rel="stylesheet" href="../static/css/debt_collection/Summary.css" data-demo-href="./static/css/debt_collection/Summary.css" />
    <script src="../static/js/content.js" data-demo-src="./static/js/demo/content.js"></script>
    <script src="../static/js/debt_collection/Summary.js"></script>
</head>
<body>
    <form id="form1" runat="server">
        <div>
            <!-- 不動産担保台帳 -->
            <asp:LinkButton
                ID="Dummy"
                runat="server"
                CssClass="js-disable-in-ref">不動産担保台帳
            </asp:LinkButton>
        </div>
        <div class="title">概況</div>
        <cc1:ISIDMessageBox ID="messageBox" runat="server"></cc1:ISIDMessageBox>
        <asp:HiddenField
            ID="hidReferenceMode"
            runat="server"
            Value="0" />
        <div class="area_content">
            <!-- 検索条件エリア -->
            <div class="content">
                <table class="grid-detail search-condition-table" data-cols="5">
                    <tr>
                        <!-- 店番・店名 -->
                        <th>
                            <label for="ddlBranchNo" data-required>店番・店名</label>
                        </th>
                        <td>
                            <asp:DropDownList
                                ID="ddlBranchNo"
                                runat="server"
                                ClientIDMode="Static"
                                CssClass="js-disable-in-ref"
                                AutoPostBack="True"
                                OnSelectedIndexChanged="ddlBranchNo_SelectedIndexChanged">
                            </asp:DropDownList>
                        </td>
                    </tr>
                    <tr>
                        <!-- 顧客番号 -->
                        <th>
                            <label for="tbxCustomerNo" data-required>顧客番号</label>
                        </th>
                        <td>
                            <asp:TextBox
                                ID="tbxCustomerNo"
                                runat="server"
                                MaxLength="12"
                                Wrap="False"
                                CssClass="js-disable-in-ref"
                                required>
                            </asp:TextBox>

                            <!-- 顧客名（表示用） -->
                            <asp:Label
                                ID="lblCustomerName"
                                runat="server"
                                CssClass="readonly"
                                Style="margin-left: 10px;">
                            </asp:Label>

                            <!-- 顧客表示ボタン -->
                            <asp:Button
                                ID="btnCustShow"
                                runat="server"
                                Text="表示"
                                CssClass="button-normal js-disable-in-ref"
                                OnClick="btnCustShow_Click"></asp:Button>

                            <!-- 顧客検索ボタン -->
                            <input
                                type="button"
                                id="btnCustSearch"
                                class="button-normal js-disable-in-ref"
                                value="検索" />

                            <!-- クリアボタン -->
                            <input
                                type="button"
                                id="btnClear"
                                class="button-normal js-disable-in-ref"
                                value="クリア" />
                        </td>
                    </tr>
                    <tr>
                        <!-- 事象ステータス -->
                        <th>
                            <label for="rblStatus">事象ステータス</label>
                        </th>
                        <td>
                            <asp:RadioButtonList
                                ID="rblJisyoStatus"
                                runat="server"
                                RepeatDirection="Horizontal"
                                CssClass="radio-list js-disable-in-ref">
                            </asp:RadioButtonList>
                        </td>
                    </tr>

                </table>
            </div>
            <!-- 債権明細エリア -->
            <div class="content">
                <div class="wrapper_grid-list">
                    <div class="grid-list-header">
                        <div>
                            <label>債権明細</label>
                        </div>
                    </div>

                    <table class="grid-list" id="list" data-sortable data-responsive>
                        <!-- ▼ ヘッダ部（ソート対応） -->
                        <thead id="tblScrollgridHeaderTable" runat="server">
                            <tr>
                                <!-- 債権番号（ソート可） -->
                                <th data-sort="string" data-col="0">
                                    <span>債権番号</span>
                                </th>

                                <!-- 稟議番号（ソート可） -->
                                <th data-sort="string" data-col="1">
                                    <span>稟議番号</span>
                                </th>

                                <!-- 科目（ソート可） -->
                                <th data-sort="string" data-col="2">
                                    <span>科目</span>
                                </th>

                                <!-- 期日（ソート可） -->
                                <th data-sort="date" data-col="3">
                                    <span>期日</span>
                                </th>

                                <!-- 貸付残高（ソート可） -->
                                <th data-sort="number" data-col="4">
                                    <span>貸付残高</span>
                                </th>

                                <!-- 以下は表示専用（ソート不可） -->
                                <th>使途/保証目的</th>
                                <th>延滞元本</th>
                                <th>延滞期間</th>

                                <!-- 問題債権（ソート可：有無順） -->
                                <th data-sort="string" data-col="8">
                                    <span>問題債権</span>
                                </th>

                                <!-- 条件変更（ソート可：無し→条1→条2） -->
                                <th data-sort="string" data-col="9">
                                    <span>条件変更</span>
                                </th>

                                <!-- 補正（ソート可：有無順） -->
                                <th data-sort="string" data-col="10">
                                    <span>補正</span>
                                </th>
                            </tr>
                        </thead>

                        <!-- ▼ データ部 -->
                        <tbody>
                            <asp:Repeater ID="rptSaikenMeisai" runat="server"
                                OnItemCommand="rptSaikenMeisai_ItemCommand">
                                <ItemTemplate>
                                    <tr>
                                        <!-- 債権番号（リンク押下で明細変更画面へ遷移） -->
                                        <td>
                                            <asp:LinkButton
                                                ID="lnkSaikenNo"
                                                runat="server"
                                                CssClass="js-disable-in-ref"
                                                CommandName="SaikenNo"
                                                CommandArgument='<%# Eval("JGskm_ShinseiNo") %>'>
                            <%# Util.HtmlEncode(Eval("JGskm_ShinseiNo")) %>
                                            </asp:LinkButton>
                                        </td>

                                        <!-- 稟議番号 -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("JGskm_KasitukeNo")) %>
                                        </td>

                                        <!-- 科目（汎用マスタ変換済み） -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("KamokuName")) %>
                                        </td>

                                        <!-- 期日 -->
                                        <td data-value='<%# Eval("JGskm_Kijitu") %>'>
                                            <%# FormatDate8(Eval("JGskm_Kijitu")) %>
                                        </td>

                                        <!-- 貸付残高（千円単位・千円未満切捨て） -->
                                        <td style="text-align: right">
                                            <%# FormatZandaka(Eval("JGskm_KasitukeZandaka")) %>
                                        </td>

                                        <!-- 使途/保証目的  -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("SitoHoshoName")) %>
                                            /
                                            <%# Util.HtmlEncode(Eval("HosyoMokutekiName")) %>
                                        </td>

                                        <!-- 延滞元本（千円単位） -->
                                        <td style="text-align: right">
                                            <%# FormatZandaka(Eval("JGskm_EntaiGanpon")) %>
                                        </td>

                                        <!-- 延滞期間 -->
                                        <td>
                                            <%# Eval("JGskm_EntaiKikan") %>
                                        </td>

                                        <!-- 問題債権（1の場合「*」表示） -->
                                        <td>
                                            <%# Convert.ToInt32(Eval("JGskm_MondaiSaikenTokutei")) == 1 ? "*" : "" %>
                                        </td>

                                        <!-- 条件変更（汎用マスタ変換済み） -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("JoukenHenkouName")) %>
                                        </td>

                                        <!-- 補正（1の場合「*」表示） -->
                                        <td>
                                            <%# Convert.ToInt32(Eval("JGskm_Hosei")) == 1 ? "*" : "" %>
                                        </td>
                                    </tr>
                                </ItemTemplate>
                            </asp:Repeater>
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- 延滞・悪化事象一覧エリア -->
            <div class="content">
                <div class="wrapper_grid-list">
                    <table class="grid-list" id="listJisho" data-sortable data-responsive>
                        <div class="grid-list-header">
                            <div>
                                <label>延滞・悪化事象一覧</label>
                            </div>
                        </div>
                        <thead>
                            <tr>
                                <th data-sort="string" data-col="0">
                                    <span>事象番号</span>
                                </th>
                                <th>事象種別</th>
                                <th data-sort="date" data-col="2">
                                    <span>発生日</span>
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            <asp:Repeater ID="rptJishoList" runat="server">
                                <ItemTemplate>
                                    <tr id="trItemRow" data-odd>
                                        <!-- 事象番号 -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("RGoam_IncidcentNo")) %>
                                        </td>

                                        <!-- 事象種別 -->
                                        <td>
                                            <%# Util.HtmlEncode(Eval("RGoam_IncidentKBN")) %>
                                        </td>

                                        <!-- 発生日 -->
                                        <td data-value='<%# Eval("RGoam_IncidentDate") %>'>
                                            <%# FormatDate8(Eval("RGoam_IncidentDate")) %>
                                        </td>
                                    </tr>
                                </ItemTemplate>
                            </asp:Repeater>
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- 概況入力エリア -->
            <div class="content">
                <table class="grid-detail summary-input-table" data-cols="2" style="width: 100%;">

                    <!-- 最終更新日 / 最終更新者 -->
                    <tr>
                        <th>
                            <label for="lblUpdateDate">最終更新日</label></th>
                        <td>
                            <asp:Label ID="lblUpdateDate" runat="server" />
                        </td>
                    </tr>
                    <tr>
                        <th>
                            <label for="lblUpdateUser">最終更新者</label></th>
                        <td>
                            <asp:Label ID="lblUpdateUser" runat="server" />
                        </td>
                    </tr>
                    <!-- 排他チェック用（更新日時保持） -->
                    <asp:HiddenField
                        ID="hidUpdateDateTime"
                        runat="server" />

                    <!-- 事故及び延滞に至った原因 -->
                    <tr>
                        <th>
                            <label for="txtReason">事故及び延滞に至った原因</label>
                        </th>
                        <td colspan="3">
                            <asp:TextBox
                                ID="txtReason"
                                runat="server"
                                TextMode="MultiLine"
                                Rows="3"
                                data-maxlength="2000"
                                Width="100%"
                                CssClass="js-disable-in-ref" />
                        </td>
                    </tr>

                    <!-- 債務者および保証人の現況 -->
                    <tr>
                        <th>
                            <label for="txtStatus">債務者および保証人の現況</label>
                        </th>
                        <td colspan="3">
                            <asp:TextBox
                                ID="txtCurrentSituation"
                                runat="server"
                                TextMode="MultiLine"
                                Rows="2"
                                data-maxlength="2000"
                                Width="100%"
                                CssClass="js-disable-in-ref" />
                        </td>
                    </tr>

                    <!-- 回収、解消の方針、スケジュール -->
                    <tr>
                        <th>
                            <label for="txtPlan">回収、解消の方針、スケジュール</label>
                        </th>
                        <td colspan="3">
                            <asp:TextBox
                                ID="txtPolicy"
                                runat="server"
                                TextMode="MultiLine"
                                Rows="1"
                                data-maxlength="2000"
                                Width="100%"
                                CssClass="js-disable-in-ref" />
                        </td>
                    </tr>

                    <!-- 備考 -->
                    <tr>
                        <th>
                            <label for="txtRemark">備考、特記事項</label>
                        </th>
                        <td colspan="3">
                            <asp:TextBox
                                ID="txtRemarks"
                                runat="server"
                                TextMode="MultiLine"
                                Rows="3"
                                data-maxlength="2000"
                                Width="100%"
                                CssClass="js-disable-in-ref" />
                        </td>
                    </tr>

                </table>

                <!-- ===== ボタンエリア ===== -->
                <div class="button-area">

                    <!-- クリア -->
                    <input
                        type="button"
                        id="btnSummaryClear"
                        class="button-normal js-disable-in-ref"
                        value="クリア" />

                    <!-- 登録 -->
                    <asp:Button
                        ID="btnRegister"
                        runat="server"
                        Text="登録"
                        CssClass="button-normal js-disable-in-ref"
                        OnClick="btnRegister_Click" />

                </div>
            </div>
            <!-- 帳票出力エリア -->
            <div class="content">
                <%--               <div class="wrapper_grid-list">
                    <div class="grid-list-header">
                        <div>
                            <label>帳票出力</label>
                        </div>
                    </div>--%>

                <table class="grid-list" id="listReport">
                    <thead>
                        <tr>
                            <th>
                                <asp:CheckBox ID="chkAllReport" runat="server" />
                            </th>
                            <th>
                                <span>帳票名</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <asp:Repeater ID="rptReportList" runat="server">
                            <ItemTemplate>
                                <tr>
                                    <td style="text-align: center;">
                                        <asp:CheckBox
                                            ID="chkReport"
                                            runat="server" />
                                        <asp:HiddenField
                                            ID="hidReportName"
                                            runat="server"
                                            Value='<%# Eval("ReportName") %>' />
                                        <asp:HiddenField
                                            ID="hidReportClass"
                                            runat="server"
                                            Value='<%# Eval("ReportClass") %>' />
                                        <asp:HiddenField
                                            ID="hidElementId"
                                            runat="server"
                                            Value='<%# Eval("ElementId") %>' />
                                        <asp:HiddenField
                                            ID="hidDefinition"
                                            runat="server"
                                            Value='<%# Eval("Definition") %>' />
                                        <asp:HiddenField
                                            ID="hidKind"
                                            runat="server"
                                            Value='<%# Eval("Kind") %>' />
                                    </td>
                                    <td>
                                        <%# Util.HtmlEncode(Eval("ReportName")) %>
                                    </td>
                                </tr>
                            </ItemTemplate>
                        </asp:Repeater>
                    </tbody>
                </table>

                <div class="button-area">
                    <asp:Button
                        ID="btnDownload"
                        runat="server"
                        Text="ダウンロード"
                        CssClass="button-normal js-disable-in-ref" />
                    <iframe id="downloadFrame" name="download" style="display:none;"></iframe>
                </div>
                <%--</div>--%>
            </div>
        </div>
    </form>
</body>
</html>
