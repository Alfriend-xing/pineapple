from sqlalchemy import Column, Integer, String,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import click
import sys


Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, index=True)    # 招聘主页地址
    jbtype = Column(String, index=True) # 工作技术名称
    city = Column(String, index=True)   # 工作地点
    creat_time = Column(String, index=True) #创建时间
    name = Column(String)   # 工作名称
    selery = Column(String) # 薪资
    exp = Column(String)    # 经验要求
    study = Column(String)  # 学历要求
    worktype = Column(String)   # 全职实习
    company = Column(String)    # 公司信息
    msg = Column(String)        # 职位指责要求

def mksession():
    if sys.platform=='win32':
        engine = create_engine(
            'sqlite:///jb.db?check_same_thread=False')
    else:
        engine = create_engine(
            'sqlite:///jb.db?check_same_thread=False')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

@click.group()
def cli():
    pass

@cli.command()
def c():
    if sys.platform=='win32':
        engine = create_engine(
            'sqlite:///jb.db?check_same_thread=False')
    else:
        engine = create_engine(
            'sqlite:///jb.db?check_same_thread=False')
    Base.metadata.create_all(engine)
    click.echo('create the database')

@cli.command()
@click.option('-n','--number' ,default=1, help='query one')
def q(number):
    click.echo('------query one------')
    session = mksession()
    jb=session.query(Job).filter_by(id=number).first()
    if jb:
        print(jb.url)
        print(jb.jbtype)
        print(jb.city)
        print(jb.creat_time)
        print('------')
        print(jb.name)
        print(jb.selery)
        # print(jb.exp)
        # print(jb.study)
        # print(jb.worktype)
        # print(jb.company)
        print(jb.msg)
    else:
        print('not found')


if __name__=="__main__":
    cli()