class Metric(object):

    id = None
    key =
    unit = Column(BigInteger, ForeignKey('entities.id')) # default 'count'
    value = 


class Event(object):
    """Revision history"""
    id = None
    oid = None
    time = None

class Resource(core.Base):

    # seen by? % consumed?

    """An Entity node can be associated with multiple Resources
    - a URL
    - a HTML document
    - an attachment (binary)
    """

    __tablename__ = "resources"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    body = Column(Unicode, unique=True, nullable=False) # url; content published elsewhere (S3)


class Checkin(core.Base):

    __tablename__ = "checkins"

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)    
