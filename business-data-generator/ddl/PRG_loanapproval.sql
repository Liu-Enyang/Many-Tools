USE [RiskTaker]
GO

/****** Object:  Table [dbo].[PRG_loanapproval]    Script Date: 2026/04/20 8:50:31 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[PRG_loanapproval](
	[RGlap_ApprovalNo] [varchar](15) NOT NULL,
	[RGlap_CustomerId] [bigint] NOT NULL,
	[RGlap_ApprovalTypeCode] [varchar](15) NOT NULL,
	[RGlap_DealingTypeCode] [varchar](15) NULL,
	[RGlap_ApprovalItemCode] [varchar](15) NULL,
	[RGlap_LmtApprovalNo] [varchar](15) NULL,
	[RGlap_LmtMoney] [money] NULL,
	[RGlap_LmtMrgMoney] [money] NULL,
	[RGlap_LmtMrgCalcBaseDate] [char](8) NULL,
	[RGlap_LmtStartDate] [char](8) NULL,
	[RGlap_LmtEndDate] [char](8) NULL,
	[RGlap_LmtInterestRate] [decimal](8, 5) NULL,
	[RGlap_RequestReceiptNo] [varchar](15) NULL,
	[RGlap_PrevApprovalNo] [varchar](15) NULL,
	[RGlap_OriginalApprovalNo] [varchar](15) NULL,
	[RGlap_SettAuthorityCode] [varchar](15) NOT NULL,
	[RGlap_ExecScheduledDate] [char](8) NOT NULL,
	[RGlap_RepaymentLimitDay] [char](8) NULL,
	[RGlap_CommodityCode] [varchar](8) NULL,
	[RGlap_SecurityDivision] [varchar](8) NULL,
	[RGlap_ExecScheduledMoney] [money] NULL,
	[RGlap_InterestRate] [decimal](8, 5) NULL,
	[RGlap_InterestRateApplyType] [varchar](15) NULL,
	[RGlap_InterestSupplyRate] [decimal](8, 5) NULL,
	[RGlap_VariableInterestCode] [varchar](15) NULL,
	[RGlap_SlideRange] [decimal](8, 5) NULL,
	[RGlap_StandardSpread] [decimal](8, 5) NULL,
	[RGlap_LoanTotal] [money] NULL,
	[RGlap_DepositTotal] [money] NULL,
	[RGlap_LoanInterestTotal] [money] NULL,
	[RGlap_DepositInterestTotal] [money] NULL,
	[RGlap_HeadBranchCalcRate] [decimal](8, 5) NULL,
	[RGlap_HeadBranchCalcDebitRate] [decimal](8, 5) NULL,
	[RGlap_HeadBranchCalcCreditRate] [decimal](8, 5) NULL,
	[RGlap_RelatedRealInterestRate] [decimal](8, 5) NULL,
	[RGlap_RelatedDpstFinanceRate] [decimal](8, 5) NULL,
	[RGlap_RelatedAnnualProfits] [money] NULL,
	[RGlap_CapitalUseDivision] [varchar](15) NULL,
	[RGlap_CapitalUseDetailDivision] [varchar](15) NULL,
	[RGlap_CapitalUseDetailDesc] [varchar](500) NULL,
	[RGlap_RaiseDetailItem1] [varchar](12) NULL,
	[RGlap_RaiseDetailItem2] [varchar](12) NULL,
	[RGlap_RaiseDetailItem3] [varchar](12) NULL,
	[RGlap_RaiseDetailMoney1] [money] NULL,
	[RGlap_RaiseDetailMoney2] [money] NULL,
	[RGlap_RaiseDetailMoney3] [money] NULL,
	[RGlap_FundsOnHandMoney] [money] NULL,
	[RGlap_RepaymentWayCode] [varchar](15) NULL,
	[RGlap_RepaymentInterestCode] [varchar](15) NULL,
	[RGlap_FirstRepayInterestDate] [char](8) NULL,
	[RGlap_FirstRepayDate] [char](8) NULL,
	[RGlap_RepayIntervalCode] [varchar](15) NULL,
	[RGlap_RepayInterestIntrvlCode] [varchar](15) NULL,
	[RGlap_RepayCapital] [varchar](500) NULL,
	[RGlap_RepayCount1] [smallint] NULL,
	[RGlap_RepayCount2] [smallint] NULL,
	[RGlap_RepayCount3] [smallint] NULL,
	[RGlap_EveryRepayMoney1] [money] NULL,
	[RGlap_EveryRepayMoney2] [money] NULL,
	[RGlap_EveryRepayMoney3] [money] NULL,
	[RGlap_SecurityFloatingExistFlg] [tinyint] NULL,
	[RGlap_SecurityDesc] [varchar](500) NULL,
	[RGlap_Remarks] [varchar](500) NULL,
	[RGlap_WideUseApprovalDtls] [varchar](500) NULL,
	[RGlap_SubTitle] [varchar](15) NULL,
	[RGlap_SubTitleSupplement] [varchar](40) NULL,
	[RGlap_ConditionCngTypeCode] [varchar](15) NULL,
	[RGlap_ConditionExmptCrdtCode] [varchar](15) NULL,
	[RGlap_ReleaseJdgmntIntrstRate] [decimal](8, 5) NULL,
	[RGlap_ApplyInterestRate] [decimal](8, 5) NULL,
	[RGlap_ConditionExemptDesc] [varchar](500) NULL,
	[RGlap_OldVersionFlag] [tinyint] NOT NULL,
	[RGlap_RegisterFlag] [tinyint] NOT NULL,
	[RGlap_RenovationFlag] [tinyint] NOT NULL,
	[RGlap_DraftDate] [datetime] NOT NULL,
	[RGlap_DraftUserName] [varchar](30) NOT NULL,
	[RGlap_SecurityCode] [varchar](8) NULL,
	[RGlap_TempFlag] [tinyint] NULL,
	[RGlap_InChargeUserNo] [char](12) NULL,
	[RGlap_InChargeUserName] [varchar](30) NULL,
	[RGlap_HQInChargeUserNo] [char](12) NULL,
	[RGlap_HQInChargeUserName] [varchar](30) NULL,
	[RGlap_ChangeStandardDate] [char](8) NULL,
	[RGlap_CreditNo] [varchar](15) NULL,
	[RGlap_BillLimitDate] [char](8) NULL,
	[RGlap_RootManagementNo] [int] NULL,
	[RGlap_SheetCount] [smallint] NULL,
	[RGlap_BonusTotalMoney] [money] NULL,
	[RGlap_ForeignMoney] [decimal](15, 2) NULL,
	[RGlap_MonetaryUnit] [varchar](15) NULL,
	[RGlap_Reservation] [varchar](15) NULL,
	[RGlap_RefinanceDivision] [varchar](15) NULL,
	[RGlap_RefinanceFirstDate] [char](8) NULL,
	[RGlap_RefinanceUseDivision] [varchar](15) NULL,
	[RGlap_SelectTypeDivision] [varchar](15) NULL,
	[RGlap_FixedContractualRate] [decimal](8, 5) NULL,
	[RGlap_VariableContractualRate] [decimal](8, 5) NULL,
	[RGlap_StepRateAppliedDate] [char](8) NULL,
	[RGlap_StepRate] [decimal](8, 5) NULL,
	[RGlap_StepPeriod] [char](2) NULL,
	[RGlap_OperateDetailItem1] [varchar](12) NULL,
	[RGlap_OperateDetailItem2] [varchar](12) NULL,
	[RGlap_OperateDetailItem3] [varchar](12) NULL,
	[RGlap_OperateDetailItem4] [varchar](12) NULL,
	[RGlap_OperateDetailItem5] [varchar](12) NULL,
	[RGlap_OperateDetailItem6] [varchar](12) NULL,
	[RGlap_OperateDetailItem7] [varchar](12) NULL,
	[RGlap_OperateDetailItem8] [varchar](12) NULL,
	[RGlap_OperateDetailItem9] [varchar](12) NULL,
	[RGlap_OperateDetailMoney1] [money] NULL,
	[RGlap_OperateDetailMoney2] [money] NULL,
	[RGlap_OperateDetailMoney3] [money] NULL,
	[RGlap_OperateDetailMoney4] [money] NULL,
	[RGlap_OperateDetailMoney5] [money] NULL,
	[RGlap_OperateDetailMoney6] [money] NULL,
	[RGlap_OperateDetailMoney7] [money] NULL,
	[RGlap_OperateDetailMoney8] [money] NULL,
	[RGlap_OperateDetailMoney9] [money] NULL,
	[RGlap_RaiseDetailItem4] [varchar](12) NULL,
	[RGlap_RaiseDetailItem5] [varchar](12) NULL,
	[RGlap_RaiseDetailItem6] [varchar](12) NULL,
	[RGlap_RaiseDetailMoney4] [money] NULL,
	[RGlap_RaiseDetailMoney5] [money] NULL,
	[RGlap_RaiseDetailMoney6] [money] NULL,
	[RGlap_RepayDay] [char](2) NULL,
	[RGlap_FractionDivision] [varchar](15) NULL,
	[RGlap_DeferInterestIntrvlCode] [varchar](15) NULL,
	[RGlap_BonusRepayMoney] [money] NULL,
	[RGlap_BonusRepayCount] [smallint] NULL,
	[RGlap_BonusBeginDate] [char](6) NULL,
	[RGlap_BonusMonth1] [char](2) NULL,
	[RGlap_BonusMonth2] [char](2) NULL,
	[RGlap_CommissionDivision] [varchar](15) NULL,
	[RGlap_GroupInsuranceDivision] [varchar](15) NULL,
	[RGlap_DebtSupport] [varchar](15) NULL,
	[RGlap_FireInsuranceFlag] [varchar](15) NULL,
	[RGlap_StartRepayDate1] [char](8) NULL,
	[RGlap_RepayDay1] [char](2) NULL,
	[RGlap_LastRepayDate1] [char](8) NULL,
	[RGlap_RepayIntervalCode1] [varchar](15) NULL,
	[RGlap_IncreaseDecreaseMoney1] [money] NULL,
	[RGlap_StartRepayDate2] [char](8) NULL,
	[RGlap_RepayDay2] [char](2) NULL,
	[RGlap_LastRepayDate2] [char](8) NULL,
	[RGlap_RepayIntervalCode2] [varchar](15) NULL,
	[RGlap_IncreaseDecreaseMoney2] [money] NULL,
	[RGlap_StartRepayDate3] [char](8) NULL,
	[RGlap_RepayDay3] [char](2) NULL,
	[RGlap_LastRepayDate3] [char](8) NULL,
	[RGlap_RepayIntervalCode3] [varchar](15) NULL,
	[RGlap_IncreaseDecreaseMoney3] [money] NULL,
	[RGlap_StartRepayDate4] [char](8) NULL,
	[RGlap_RepayDay4] [char](2) NULL,
	[RGlap_LastRepayDate4] [char](8) NULL,
	[RGlap_RepayIntervalCode4] [varchar](15) NULL,
	[RGlap_IncreaseDecreaseMoney4] [money] NULL,
	[RGlap_StartRepayDate5] [char](8) NULL,
	[RGlap_RepayDay5] [char](2) NULL,
	[RGlap_LastRepayDate5] [char](8) NULL,
	[RGlap_RepayIntervalCode5] [varchar](15) NULL,
	[RGlap_IncreaseDecreaseMoney5] [money] NULL,
	[RGlap_RelatedLoanTotal] [money] NULL,
	[RGlap_RelatedDepositTotal] [money] NULL,
	[RGlap_RelatedLoanInterestTotal] [money] NULL,
	[RGlap_RelatedDpstInterestTotal] [money] NULL,
	[RGlap_DraftBranchNo] [char](4) NULL,
	[RGlap_DraftBranchName] [varchar](20) NULL,
	[RGlap_ExecutionBranchNo] [char](4) NULL,
	[RGlap_StaffFinanceFlag] [tinyint] NULL,
	[RGlap_ScheduledCloseMoney] [money] NULL,
	[RGlap_SimulScheduledCloseMoney] [money] NULL,
	[RGlap_DepositSecurityMny] [money] NULL,
	[RGlap_SimulDepositSecurityMny] [money] NULL,
	[RGlap_SocietyLoadMoney] [money] NULL,
	[RGlap_SimulSocietyLoadMoney] [money] NULL,
	[RGlap_AutoJudgeSettAuthority] [varchar](15) NULL,
	[RGlap_SettAuthorityJudgeDate] [datetime] NULL,
	[RGlap_SettAuthorityJudgeReason] [varchar](255) NULL,
	[RGlap_RespShareDivision] [varchar](15) NULL,
	[RGlap_ReceiptYear] [char](4) NULL,
	[RGlap_FixedIntstRateSelectDate] [char](8) NULL,
	[RGlap_AppSlipErrFlag] [tinyint] NOT NULL,
	[RGlap_BasisCondUpdateTime] [datetime] NOT NULL,
	[RGlap_AutoCalcEveryRepayMoney2] [money] NULL,
	[RGlap_AutoCalcBonusRepayMoney] [money] NULL,
	[RGlap_TempAdmitFlag] [tinyint] NOT NULL,
	[RGlap_ChushinSecurityFlag] [tinyint] NOT NULL,
	[RGlap_ReapplicationCode] [varchar](15) NULL,
	[RGlap_EstablishmentSupport] [varchar](15) NULL,
	[RGlap_BusinessAssessment] [varchar](15) NULL,
	[RGlap_ReapplyPrevApprovalNo] [varchar](15) NULL,
	[RGlap_BackinApproval] [tinyint] NULL,
	[RGlap_RateDownCreditNo] [varchar](15) NULL,
	[RGlap_NowSelectTypeDivision] [varchar](15) NULL,
	[RGlap_NowInterestRate] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision1] [varchar](15) NULL,
	[RGlap_SelectTypeRate1] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision2] [varchar](15) NULL,
	[RGlap_SelectTypeRate2] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision3] [varchar](15) NULL,
	[RGlap_SelectTypeRate3] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision4] [varchar](15) NULL,
	[RGlap_SelectTypeRate4] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision5] [varchar](15) NULL,
	[RGlap_SelectTypeRate5] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision6] [varchar](15) NULL,
	[RGlap_SelectTypeRate6] [decimal](8, 5) NULL,
	[RGlap_SelectTypeDivision7] [varchar](15) NULL,
	[RGlap_SelectTypeRate7] [decimal](8, 5) NULL,
	[RGlap_ConditionApprovalFlag] [tinyint] NOT NULL,
	[InsertDateTime] [datetime] NOT NULL,
	[InsertUserNo] [char](12) NOT NULL,
	[UpdateDateTime] [datetime] NOT NULL,
	[UpdateUserNo] [char](12) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RGlap_ApprovalNo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_OldVersionFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_RegisterFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_RenovationFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_TempFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_AppSlipErrFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT (getdate()) FOR [RGlap_BasisCondUpdateTime]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_TempAdmitFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_ChushinSecurityFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_BackinApproval]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT ((0)) FOR [RGlap_ConditionApprovalFlag]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT (getdate()) FOR [InsertDateTime]
GO

ALTER TABLE [dbo].[PRG_loanapproval] ADD  DEFAULT (getdate()) FOR [UpdateDateTime]
GO

