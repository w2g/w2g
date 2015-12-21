class Milestone(object):
    """A tagged release"""

    id = None
    oid = None
    tasks = []


class Task(object):
    """A branch"""

    id = None
    oid = None
    steps = []


class Step(object):
    """A rebased feature commit"""

    id = None
    oid = None
    details = []
    # sub-steps? dependencies?

class Detail(object):
    """A commit"""

    id = None
    oid = None
    status = False
    time_est = 0


class Post(object):

    __tablename__ = "posts"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    title = Column(Unicode)
    body = Column(Unicode)
    #hash = "" # url-safe slug
    # creator = Column(BigInteger, ForeignKey('users.id'))
    label = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

