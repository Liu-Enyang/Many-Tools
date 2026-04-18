USE [RiskTaker]
GO

/****** Object:  Table [dbo].[PJG_saikenmeisai]    Script Date: 2026/04/03 8:59:46 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[PJG_saikenmeisai](
	[JGskm_SyoriId] [char](16) NOT NULL,
	[JGskm_BranchNo] [char](4) NOT NULL,
	[JGskm_CustomerNo] [char](12) NOT NULL,
	[JGskm_KijyunNengetu] [char](6) NOT NULL,
	[JGskm_ShinseiNo] [bigint] NOT NULL,
	[JGskm_KasitukeNo] [int] NOT NULL,
	[JGskm_Kamoku] [varchar](15) NOT NULL,
	[JGskm_Riritu] [decimal](8, 5) NULL,
	[JGskm_ShinseiDate] [char](8) NULL,
	[JGskm_ShinseiKigen] [char](8) NULL,
	[JGskm_TousyoJikkouDate] [char](8) NULL,
	[JGskm_Kijitu] [char](8) NULL,
	[JGskm_SyoninKigen] [char](8) NULL,
	[JGskm_KasitukeZandaka] [money] NULL,
	[JGskm_TousyoJikkouKingaku] [money] NULL,
	[JGskm_SikinSito] [varchar](15) NULL,
	[JGskm_HosyoMokuteki] [varchar](15) NULL,
	[JGskm_HensaiHouhou] [varchar](15) NULL,
	[JGskm_SyokaiHensaiDate] [char](8) NULL,
	[JGskm_SyokaiHensaigaku] [money] NULL,
	[JGskm_TotyukaiHensaigaku] [money] NULL,
	[JGskm_SaisyukaiHensaigaku] [money] NULL,
	[JGskm_HensaiSyuki] [smallint] NULL,
	[JGskm_EntaiGanpon] [money] NULL,
	[JGskm_EntaiKikan] [smallint] NULL,
	[JGskm_MondaiSaikenTokutei] [tinyint] NULL,
	[JGskm_JoukenHenkou] [varchar](15) NULL,
	[JGskm_KjkKanwaSaiken] [varchar](15) NULL,
	[JGskm_KengenKubun] [varchar](15) NULL,
	[JGskm_HimotukiTanpo] [varchar](15) NULL,
	[JGskm_HimotukiHosyo] [varchar](15) NULL,
	[JGskm_Bikou] [varchar](256) NULL,
	[JGskm_Tokukasi1HendouKingaku] [money] NULL,
	[JGskm_Tokukasi1HendouJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi1HendouComment] [varchar](30) NULL,
	[JGskm_Tokukasi2HendouKingaku] [money] NULL,
	[JGskm_Tokukasi2HendouJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi2HendouComment] [varchar](30) NULL,
	[JGskm_Tokukasi3HendouKingaku] [money] NULL,
	[JGskm_Tokukasi3HendouJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi3HendouComment] [varchar](30) NULL,
	[JGskm_Tokukasi4HendouKingaku] [money] NULL,
	[JGskm_Tokukasi4HendouJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi4HendouComment] [varchar](30) NULL,
	[JGskm_Tokukasi1KoteiKingaku] [money] NULL,
	[JGskm_Tokukasi1KoteiJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi1KoteiComment] [varchar](30) NULL,
	[JGskm_Tokukasi2KoteiKingaku] [money] NULL,
	[JGskm_Tokukasi2KoteiJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi2KoteiComment] [varchar](30) NULL,
	[JGskm_Tokukasi3KoteiKingaku] [money] NULL,
	[JGskm_Tokukasi3KoteiJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi3KoteiComment] [varchar](30) NULL,
	[JGskm_Tokukasi4KoteiKingaku] [money] NULL,
	[JGskm_Tokukasi4KoteiJiyu] [varchar](15) NULL,
	[JGskm_Tokukasi4KoteiComment] [varchar](30) NULL,
	[JGskm_Hosei] [tinyint] NOT NULL,
	[JGskm_LoanFlg] [tinyint] NOT NULL,
	[JGskm_SyohinCode] [varchar](8) NULL,
	[JGskm_TanpoCode] [varchar](6) NULL,
	[JGskm_RisokuDate] [char](8) NULL,
	[JGskm_KyokudoFlg] [tinyint] NULL,
	[JGskm_BISShikibetsu1] [varchar](15) NULL,
	[JGskm_BISShikibetsu2] [varchar](15) NULL,
	[JGskm_SinkiTourokuDate] [datetime] NOT NULL,
	[JGskm_SinkiTourokuUserNo] [char](10) NOT NULL,
	[JGskm_LastUpdate] [datetime] NULL,
	[JGskm_UpdateUserNo] [char](10) NULL,
PRIMARY KEY CLUSTERED 
(
	[JGskm_SyoriId] ASC,
	[JGskm_ShinseiNo] ASC,
	[JGskm_KasitukeNo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[PJG_saikenmeisai] ADD  DEFAULT (NULL) FOR [JGskm_BISShikibetsu1]
GO

ALTER TABLE [dbo].[PJG_saikenmeisai] ADD  DEFAULT (NULL) FOR [JGskm_BISShikibetsu2]
GO

