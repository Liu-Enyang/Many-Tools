USE [RiskTaker]
GO

/****** Object:  Table [dbo].[PRM_incidentlistmapping]    Script Date: 2026/04/03 12:30:58 ******/
SET ANSI_NULLS OFF
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[PRM_incidentlistmapping](
	[RGoam_IncidcentNo] [char](15) NOT NULL,
	[RGoam_SaikenNo] [varchar](15) NULL,
	[RGoam_BranchNo] [char](4) NOT NULL,
	[RGoam_BranchName] [varchar](30) NULL,
	[RGoam_CustomerNo] [char](12) NOT NULL,
	[RGoam_CustomerName] [varchar](70) NULL,
	[RGoam_IncidentKBN] [varchar](15) NULL,
	[RGoam_IncidentDate] [char](8) NULL,
	[RGoam_Nissuu] [smallint] NULL,
	[RGoam_IncidentStutusKBN] [varchar](15) NULL,
	[InsertDateTime] [datetime] NULL,
	[InsertUserNo] [char](12) NULL,
	[UpdateDateTime] [datetime] NOT NULL,
	[UpdateUserNo] [char](12) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RGoam_IncidcentNo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

