USE [RiskTaker]
GO

/****** Object:  Table [dbo].[PCC_hanyou]    Script Date: 2026/04/20 8:48:53 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[PCC_hanyou](
	[CChny_HanyouUniqueKey] [varchar](15) NOT NULL,
	[CChny_HanyouCodeKey] [varchar](20) NOT NULL,
	[CChny_Sort] [smallint] NOT NULL,
	[CChny_HanyouCodeValue] [varchar](15) NOT NULL,
	[CChny_HanyouCodeNaiyou] [varchar](20) NOT NULL,
	[CChny_HanyouCodeSetumei] [varchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[CChny_HanyouUniqueKey] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

