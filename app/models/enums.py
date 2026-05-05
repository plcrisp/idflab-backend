import enum

class BiasCorrectionEnum(str, enum.Enum):
    NONE = "NONE"
    QM = "QM"
    DBC = "DBC"
    EQM = "EQM"

class UserTypeEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    RESEARCHER = "RESEARCHER"
    PROFESSOR = "PROFESSOR"

class LoginProviderEnum(str, enum.Enum):
    GOOGLE = "GOOGLE"
    LOCAL = "LOCAL"
    BOTH = "BOTH"

class ScenarioEnum(str, enum.Enum):
    HISTORICAL = "HISTORICAL"
    SSP245 = "SSP245"
    SSP585 = "SSP585"

class DistributionEnum(str, enum.Enum):
    NORMAL = "NORMAL"
    LOGNORMAL = "LOGNORMAL"
    PARETO = "PARETO"
    GUMBEL_R = "GUMBEL_R"
    GEV = "GEV"
    GENLOGISTIC = "GENLOGISTIC"

class SourceEnum(str, enum.Enum):
    CEMADEN = "CEMADEN"
    INMET = "INMET"

class DisaggregationEnum(str, enum.Enum):
    NONE = "NONE"
    CETESB = "CETESB"
    BL = "BL"

class TaskTypeEnum(str, enum.Enum):
    DOWNLOAD_STATION_DATA = "DOWNLOAD_STATION_DATA"
    GAP_FILLING = "GAP_FILLING"
    QUALITY_ANALYSIS = "QUALITY_ANALYSIS"
    GENERATE_IDF = "GENERATE_IDF"
    DOWNLOAD_CLIMBRA = "DOWNLOAD_CLIMBRA"
    BIAS_CORRECTION = "BIAS_CORRECTION"
    GENERATE_REPORT = "GENERATE_REPORT"

class StatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"