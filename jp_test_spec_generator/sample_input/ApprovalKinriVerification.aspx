<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="ApprovalKinriVerification.aspx.cs" Inherits="Isid.RiskTaker.Web.ApprovalKinriVerification" %>

<%@ Register TagPrefix="cc1" Namespace="Isid.RiskTaker.Common.UI" Assembly="Isid.RiskTaker.Common" %>
<%@ Register TagPrefix="cc3" Namespace="Isid.RiskTaker.Common.UI.ConfirmButton" Assembly="Isid.RiskTaker.Common" %>
<%@ Import Namespace="Isid.RiskTaker.Common.Utility" %>
<%@ Import Namespace="Isid.RiskTaker.Common.Info" %>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ApprovalKinriVerification</title>
    <%-- Message Box --%>
    <cc1:ISIDMessageBox ID="messageBox" runat="server"></cc1:ISIDMessageBox>
    <link rel="stylesheet" href="../static/css/content.min.css" data-demo-href="./static/css/content.min.css" />
    <link rel="stylesheet" href="../static/css/approval/ApprovalKinriVerification.css" data-demo-href="./static/css/approval/ApprovalKinriVerification.css" />
    <script src="../static/js/content.js" data-demo-src="./static/js/demo/content.js"></script>
</head>
<body>
    <form id="ApprovalKinriVerification" method="post" runat="server">
        <div class="title">適正金利検証</div>
        <div class="area_content">
            <div class="content-title">本件申請内容</div>
            <div class="content">
                <table class="grid-detail" id="detail01Table">
                    <tbody>
                        <tr>
                            <th><label for="ddlRGkvcGrading" data-required>格付</label></th>
                            <td>
                                <asp:DropDownList ID="ddlRGkvcGrading" runat="server"></asp:DropDownList></td>
                            <th><label for="ddlVariableInterestCode" data-required>金利区分</label></th>
                            <td>
                                <asp:DropDownList ID="ddlVariableInterestCode" runat="server"></asp:DropDownList>
                            </td>
                        </tr>
                        <tr>
                            <th><label for="tbxExecScheduledMoney" data-required>申請金額(千円)</label></th>
                            <td>
                                <asp:TextBox ID="tbxExecScheduledMoney" data-type="money" min="1" max="9999999" data-scale="0" step="1" size="9" runat="server"></asp:TextBox></td>
                            <th><label for="tbxFixedIntstRatePeriod">固定金利期間(ヶ月)</label></th>
                            <td>
                                <asp:TextBox ID="tbxFixedIntstRatePeriod" data-type="decimal" min="1" max="999" data-scale="0" step="1" size="3" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxInterestRate" data-required>申請金利(%)</label></th>
                            <td>
                                <asp:TextBox ID="tbxInterestRate" data-type="decimal" min="0" max="99.999" data-scale="3" step="0.001" size="6" runat="server"></asp:TextBox></td>
                            <td colspan="2">*固定金利期間が端数の場合は（日数がある場合は）、切り捨てること</td>
                        </tr>
                        <tr>
                            <th><label for="ddlCapitalUseDivision" data-required>資金使途</label></th>
                            <td>
                                <asp:DropDownList ID="ddlCapitalUseDivision" runat="server"></asp:DropDownList>
                            </td>
                            <th><label for="tbxGuaranteeJika" data-required>本件追加担保・保証時<br>価額(千円)</label></th>
                            <td>
                                <asp:TextBox ID="tbxGuaranteeJika" data-type="money" min="0" max="9999999" data-scale="0" step="1" size="9" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th>収益スプレッド(%)</th>
                            <td>
                                <asp:Label ID="lblRevenueSpread" runat="server"></asp:Label>
                            </td>
                            <td colspan="2">*保証協会保証の負担金対象の場合は、申請の80%を入力のこと</td>
                        </tr>
                        <tr>
                            <td rowspan="2" colspan="2"></td>
                            <th><label for="tbxGuaranteeYoryoku" data-required>既存担保・保証時価<br>余力額(千円)</label></th>
                            <td>
                                <asp:TextBox ID="tbxGuaranteeYoryoku" data-type="money" min="0" max="9999999" data-scale="0" step="1" size="9" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <td colspan="2">*本件追加担保＋既存保証の合計は、申請金額以内とします</td>
                        </tr>
                        <tr>
                            <th>案件保全率(時価ベース)(%)</th>
                            <td>
                                <asp:Label ID="lblCaseRetentionRate" runat="server"></asp:Label></td>
                            <th>採用標準金利(%)</th>
                            <td>
                                <asp:Label ID="lblStandardIntrstRate" runat="server"></asp:Label></td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                案件毎信用コスト＝{(100-案件保全率)*倒産確率}/100<br>
                                <asp:Label ID="lblShinyoCostShiki" class="margin-left-93" runat="server"></asp:Label>
                            </td>
                            <td colspan="2">
                                採用標準金利＝事業性標準金利(金利区分毎)＋新規経費率<br>
                                <asp:Label ID="lblStdInterestRateShiki" class="margin-left-78" runat="server"></asp:Label>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <table class="grid-detail" id="detail02Table">
                    <caption>
                        <span>金利算出結果</span>
                    </caption>
                    <tbody>
                        <tr>
                            <th>A:貸出金利(%)</th>
                            <td>
                                <asp:Label ID="lblCalculateInterestRate" runat="server"></asp:Label></td>
                            <th>B:本件申請金利(%)</th>
                            <td>
                                <asp:Label ID="lblApplicationIntrstRate" runat="server"></asp:Label></td>
                        </tr>
                        <tr>
                            <td colspan="4">
                                <div>貸出金利</div>
                                <div class="padding-left-20">
                                    標準金利＋案件毎信用コスト＋間接経費率＋収益スプレッド＋業種・資金使途・エリア要件
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="4">
                                <div>本件</div>
                                <div class="padding-left-20">
                                    <asp:Label ID="lblOutputArea" runat="server"></asp:Label>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th>乖離幅(A-B)(%)</th>
                            <td>
                                <asp:Label ID="lblDeviationRange" runat="server"></asp:Label></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="content-title">申請金利についての所見</div>
            <div class="grid-footer">※本申請金利が無出金利を下回る場合は、必ずその根拠を所見に記載のこと</div>
            <div class="content">
                <table class="grid-detail" id="detail03Table">
                    <tbody>
                        <tr>
                            <td>
                                <asp:TextBox ID="tbxFindings" runat="server" NAME="Textbox1" TextMode="MultiLine"></asp:TextBox></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="content-title">店舗用提要入力項目</div>
            <div class="content">
                <table class="grid-detail">
                    <caption>
                        <span>返済条件情報</span>
                    </caption>
                    <tbody>
                        <tr>
                            <td colspan="2">１．返済条件の有無</td>
                        </tr>
                        <tr>
                            <td class="text-center"><label for="rbtNone">無</label></td>
                            <td class="text-center"><label for="rbtHave">有</label></td>
                        </tr>
                        <tr class="grid-radio">
                            <td data-caution>
                                <asp:RadioButton ID="rbtNone" runat="server" GroupName="rbtRepaymentTermFlg" /></td>
                            <td data-caution>
                                <asp:RadioButton ID="rbtHave" runat="server" GroupName="rbtRepaymentTermFlg" /></td>
                        </tr>
                    </tbody>
                </table>

                <table class="grid-detail" id="detail04Table">
                    <tbody>
                        <tr>
                            <td colspan="4">２．返済条件が「有」の場合入力してください</td>
                        </tr>
                        <tr>
                            <th><label for="tbxAccountNumber1">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber1" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                            <th><label for="tbxAccountNumber6">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber6" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxAccountNumber2">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber2" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                            <th><label for="tbxAccountNumber7">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber7" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxAccountNumber3">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber3" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                            <th><label for="tbxAccountNumber8">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber8" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxAccountNumber4">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber4" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                            <th><label for="tbxAccountNumber9">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber9" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxAccountNumber5">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber5" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                            <th><label for="tbxAccountNumber10">口座番号</label></th>
                            <td>
                                <asp:TextBox ID="tbxAccountNumber10" data-type="numeric" maxLength="15" runat="server"></asp:TextBox></td>
                        </tr>
                        <tr>
                            <th><label for="tbxRepaymentTermTotal">返済条件合計金額(千円)</label></th>
                            <td colspan="3">
                                <asp:TextBox ID="tbxRepaymentTermTotal" data-type="money" min="0" max="9999999" data-scale="0" step="1" size="9" runat="server"></asp:TextBox></td>
                        </tr>
                    </tbody>
                </table>
                <div class="grid-footer">※「返済口座の最終返済日」が「今回新規に実行する貸出の実行日から40日後」より前の場合は、返済条件金額を「0」としてください。</div>

                <table class="grid-detail" id="detail06Table">
                    <caption>
                        <span>本件情報</span>
                    </caption>
                    <tbody>
                        <tr>
                            <th><label for="tbxLoanPeriod">貸出期間(月数)(ヶ月)</label></th>
                            <td>
                                <asp:TextBox ID="tbxLoanPeriod" data-type="decimal" min="1" max="999" data-scale="0" step="1" size="3" runat="server"></asp:TextBox></td>
                        </tr>
                    </tbody>
                </table>
                <div class="area_button">
                    <cc3:ConfirmButton CssClass="button-normal" ID="btnClear" runat="server" OnClick="btnClear_Click"></cc3:ConfirmButton>
                    <asp:Button CssClass="button-normal" ID="btnCalculate" runat="server" Text="計算" OnClick="btnCalculate_Click" />
                </div>
            </div>
            <div class="content-title">店舗評定「事業性新規貸出金収益」</div>
            <div class="content">
                <table class="grid-detail" id="detail05Table">
                    <tbody>
                        <tr>
                            <th>真水金額(千円)</th>
                            <td>
                                <asp:Label ID="lblMamizuMoney" runat="server"></asp:Label></td>
                            <th>貸出金利収益(千円)</th>
                            <td>
                                <asp:Label ID="lblLoanKinriSyueki" runat="server"></asp:Label></td>
                        </tr>
                    </tbody>
                </table>
                <table class="grid-detail" id="detail07Table">
                    <tbody>
                        <tr>
                            <th colspan="2">貸出金収益の計算式</th>
                        </tr>
                        <tr>
                            <th data-text-vertical>計算式</th>
                            <td>
                                <asp:Label ID="lblCalculate" runat="server">
                                    （申請金額－返済条件合計金額）×評定対象金利<br>
                                     　※貸出期間が12ヶ月未満の場合は、<br>
                                     　｛（申請金額－返済条件合計金額）×申請金利｝×貸出期間/12<br>
                                     　※評定対象金利<br>
                                     　　評定対象金利＝申請金利－事業性標準金利（金利区分毎）－案件毎の信用コスト－業種・資金使途・エリア要件
                                </asp:Label>
                            </td>
                        </tr>
                        <tr>
                            <th class="height-50" data-text-vertical>本件</th>
                            <td>
                                <asp:Label ID="lblCalculationDetails" runat="server"></asp:Label></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="area_button">
                <asp:Button CssClass="button-caution" ID="btnRegist" runat="server" Text="登録" OnClick="btnRegist_Click" />
            </div>
        </div>
        <asp:HiddenField ID="calculateFlgHidden" runat="server" />
    </form>
    <script src="../static/js/approval/ApprovalKinriVerification.js" data-demo-src="./static/js/demo/approval/ApprovalKinriVerification.js"></script>
</body>
</html>
