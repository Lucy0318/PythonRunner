from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    userid = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    locationid = Column(Integer, nullable=False)
    roleid = Column(Integer, nullable=False)
    full_name = Column(String(50))
    deactivated = Column(Boolean)


class Product(Base):
    __tablename__ = 'product'

    productid = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)


class Platform(Base):
    __tablename__ = 'platform'

    platformid = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    alias = Column(String(30))
    productid = Column(Integer, ForeignKey('product.productid'))
    obsolete = Column(Boolean)


class ApTestSessionGroup(Base):
    __tablename__ = 'aptest_session_group'

    aptest_session_groupid = Column(Integer, primary_key=True)
    scmlabel = Column(String(50), nullable=False)
    group_name = Column(String(100), nullable=False)
    productid = Column(Integer, nullable=False)


class TestSuite(Base):
    __tablename__ = 'test_suite'

    testsuiteid = Column(Integer, primary_key=True)
    display_name = Column(String(200), nullable=False)
    testcases = Column(Integer, nullable=False)
    exectime = Column(Integer, nullable=False)
    statusid = Column(Integer, nullable=False)
    ownerid = Column(Integer, ForeignKey('user.userid'))
    path = Column(String(400), nullable=False)
    testplan = Column(String(400))
    job_requestids = Column(String(200), nullable=False)
    moddate = Column(DateTime, nullable=False)
    adddate = Column(DateTime, nullable=False)
    platform_groupid = Column(Integer)
    feature_groupid = Column(Integer)
    scopeid = Column(Integer, nullable=False)
    scope_note = Column(String(500))
    remark = Column(String(500))
    backup_ownerid = Column(Integer, ForeignKey('user.userid'))
    featureid = Column(Integer)
    productid = Column(Integer)
    topology_definition = Column(String(400))
    openstack_ready = Column(Boolean)
    bvt = Column(Boolean)
    test_areaid = Column(Integer)
    platform_dependent = Column(Boolean)


class TestBed(Base):
    __tablename__ = 'testbed'

    tbid = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    qbs_serverid = Column(Integer, nullable=False)
    locationid = Column(Integer, nullable=False)
    user_groupid = Column(Integer)
    statusid = Column(Integer, nullable=False)
    feature_groupid = Column(Integer)
    platform_groupid = Column(Integer)
    tb_diagram = Column(String(400))
    alias = Column(String(50))
    tb_config = Column(String(400))
    remark = Column(String(400))
    locked_by = Column(Integer)
    openstack_status = Column(String(400))
    tb_type = Column(String(100))


class JobRequest(Base):
    __tablename__ = 'job_request'

    job_requestid = Column(Integer, Sequence('job_request_job_requestid_seq'), primary_key=True)
    qbsjobid = Column(Integer)
    jobname = Column(String(100))
    qbs_serverid = Column(Integer, nullable=False)
    requested_by = Column(Integer, ForeignKey('user.userid'))
    suiteid = Column(Integer)
    command = Column(String(2000), nullable=False)
    platformid = Column(Integer)
    tbid = Column(Integer)
    scmlabel = Column(String(200))
    log_location = Column(String(1000))
    requested_time = Column(DateTime, nullable=False)
    start_time = Column(DateTime)
    build_file = Column(String(1000))
    topology_id = Column(Integer)


class TestResult(Base):
    __tablename__ = 'test_result'

    resultid = Column(Integer, Sequence('test_result_resultid_seq'), primary_key=True)
    matrixid = Column(Integer)
    job_requestid = Column(Integer, nullable=False)
    type = Column(String(30), nullable=False)
    title = Column(String(500))
    parameters = Column(String(2000))
    alias = Column(String(500))
    result = Column(String(20), nullable=False)
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    filename = Column(String(500))
    log_link = Column(String(2000))
    uuid = Column(String(100))


class TestFailure(Base):
    __tablename__ = 'test_failure'
    failureid = Column(Integer, Sequence('test_failure_failureid_seq'), primary_key=True)
    ftypeid = Column(Integer, nullable=False)
    freason = Column(String(100))
    ownerid = Column(Integer)
    dtsid = Column(Integer)
    resultid = Column(Integer)
    jira = Column(String(64))


class FailureType(Base):
    __tablename__ = 'failure_type'
    ftypeid = Column(Integer, Sequence('failure_type_ftypeid_seq'), primary_key=True)
    name = Column(String(40))
    
# if __name__ == '__main__':
#     from sqlalchemy import create_engine
#     from sqlalchemy.orm import sessionmaker
#     from urllib import parse
#     db_string = "postgres://sonicauto:%s@10.203.15.9:5432/sonicauto" % parse.unquote('s0nicw@ll')
#     db = create_engine(db_string)
#     Session = sessionmaker(db)
#     session = Session()
#     # suites = session.query(TestSuite).filter(TestSuite.path == '//depot/SQA/SWIFT4.0/TESTS/Application/GMS')
#     # users = session.query(User).filter(User.userid == suites[0].ownerid)
#     # print(users[0].name)
#     # session.close()
#     ts = TestSuite()
#     ts.display_name = "PythonRunnerEmailUtilTest"
#     ts.testcases = 1
#     ts.exectime = 1
#     ts.statusid = 1
#     ts.ownerid = 317
#     ts.path = "//depot/SQA/SWIFT4.0/PythonRunner/examples/eu_test_suite.py"
#     ts.job_requestids = "143288,143299,143300"
#     ts.adddate = "2019-04-08 15:12:00"
#     ts.moddate = "2019-04-08 15:12:30"
#     ts.scopeid = 4
#     ts.backup_ownerid = 234
#
#     session.add(ts)
#     session.commit()
#     session.refresh(ts)
#     print(ts)

