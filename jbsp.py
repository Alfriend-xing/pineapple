#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from module import Job,mksession
from sqlalchemy.exc import IntegrityError
import click


fmt=logging.Formatter('%(asctime)s-%(levelname)s::%(message)s')
logger=logging.getLogger('broswer')
logger.setLevel(logging.INFO)
h1=logging.StreamHandler()
h1.setFormatter(fmt)
h1.setLevel(logging.INFO)
h2=logging.FileHandler('broswer.log', mode='a', encoding='utf-8')
h2.setFormatter(fmt)
h2.setLevel(logging.INFO)
logger.addHandler(h1)
logger.addHandler(h2)


ujson=[
    {'url':"https://www.lagou.com/",
    'input':['id',"search_input"],
    'button':[['class','tab focus']]},
    {'url':"https://www.51job.com/",
    'input':['id',"kwdselectid"],
    'button':[]},
    {'url':"https://www.zhipin.com/",
    'input':['name',"query"],
    'button':[]},
]

jbs=['java','python']  # python'java','c++','php','go','测试工程师','测试开发','运维'

citys=['北京','上海','杭州','全国']    # '深圳','广州','成都','南京','武汉','苏州'

def get_broswer():
    # 指定参数获取浏览器对象
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    return browser

def waitpage(browser):
    time.sleep(5)
    WebDriverWait(browser, 10).until(lambda x: x.find_element_by_tag_name("title"))

def fixpage(browser):
    if 'passport.lagou.com' in browser.current_url:
        browser.delete_cookie('user_trace_token')
        return 1
        # browser.delete_all_cookies()
        # browser.back()
        # logger.warning('clear cookies')
    elif 'verify.html' in browser.current_url:
        key=input('input key:')
        browser.find_element(by='id',value='code').send_keys(key)
        b=browser.find_element_by_class_name('btn')
        b.click()
        print('输入了验证码')
        time.sleep(1)
        waitpage(browser)
        return 2
    else:
        return False
        
def get_lagouwang(j_name,j_city):
    # 查询拉勾网数据
    browser=get_broswer()
    session = mksession()
    u=ujson[0]
    logger.info('start lagou with %s/%s'%(j_name,j_city))
    browser.get(u['url'])
    browser.add_cookie({'name' :'index_location_city','value' :'%E5%85%A8%E5%9B%BD'})
    browser.refresh()
    waitpage(browser)
    logger.info('loading home page')
    browser.find_element(by=u['input'][0],value=u['input'][1]).send_keys('%s'%j_name+Keys.ENTER)
    waitpage(browser)
    fixpage(browser)
    a_new=browser.find_elements_by_tag_name('a')
    for i in a_new:
        if i.text==j_city:
            i.click()
            break
    waitpage(browser)
    a_new=browser.find_elements_by_tag_name('a')
    for i in a_new:
        if i.text=='最新':
            i.click()
            time.sleep(3)
            break
    waitpage(browser)
    for pg in range(30):
        links=browser.find_elements_by_class_name('position_link')
        times=browser.find_elements_by_class_name('format-time')
        hurry=browser.find_elements_by_class_name('hurry_up')
        with open('res','a',encoding="utf-8") as f:
            for i in range(len(links)):
                if ':' in times[i].text:
                    onejob=Job(
                        url = links[i].get_property('href'),
                        jbtype = j_name,
                        city = j_city,
                        creat_time = time.strftime('%m-%d'),
                    )
                    try:
                        session.add(onejob)
                        session.commit()
                    except IntegrityError:
                        logger.warning('jb url重复%s'%links[i].get_property('href'))
                        session.rollback()
                        if j_city=='全国':
                            continue
                        else:
                            continue
                            browser.quit()
                            return
                    # f.write(links[i].get_property('href')+'\n') # times[i].text[:5]+' '+
                else:
                    if len(hurry)>0:
                        continue
                    else:
                        # 页面无急招信息且无当天发布的招聘信息
                        browser.quit()
                        return
                # logger.info('get a job link %s'%link.get_property('href'))
        # 翻页动作由ajax完成 请求前 页面已完成载入，所以无法使用wait等待下页信息载入
        try:
            nextpg=browser.find_element_by_class_name('pager_next')
            nextpg.click()
            time.sleep(5)
        except:
            logging.error("can't find nextpage botton")
    browser.quit()
    logger.info('finish lagou with %s/%s %spages'%(j_name,j_city,pg))

def get_jobinfo():
    session = mksession()
    browser = webdriver.Chrome()
    waitmsgjob=session.query(Job).filter_by(name=None).first()
    while waitmsgjob:
        line=waitmsgjob.url
        browser.get(line.strip())
        waitpage(browser)
        print('finish load')
        time.sleep(1)
        if 'passport.lagou.com' in browser.current_url:
            # key=input('input key:')
            # browser.delete_all_cookies()
            browser.delete_cookie('user_trace_token')
            browser.get(line.strip())
            waitpage(browser)
            print('delete cookies finish load')
        fixpage(browser)
        try:
            jb_name=browser.find_element_by_class_name('name').text
            jb_reqs=browser.find_element_by_class_name('job_request').text.split('\n')[0].split('/')
            jb_salary=jb_reqs[0].strip()
            jb_city=jb_reqs[1].strip()
            jb_exp=jb_reqs[2].strip()
            jb_study=jb_reqs[3].strip()
            jb_type=jb_reqs[4].strip()
            jb_msg=browser.find_element_by_class_name('job_bt').text
            jb_com=browser.find_element_by_class_name('job_company').text
        except:
            browser.refresh()
            continue
        session.query(Job).filter_by(url=line).update(
            {Job.name : jb_name,
            Job.selery : jb_salary,
            Job.exp : jb_exp,
            Job.study : jb_study,
            Job.worktype : jb_type,
            Job.company : jb_com,
            Job.msg : jb_msg,}
            )
        session.commit()
        waitmsgjob=session.query(Job).filter_by(name=None).first()
        # with open('res1','a',encoding="utf-8") as f:
        #     f.write('-------------------\n')
        #     f.write(jb_name+'\n')
        #     f.write(jb_salary+'\n')
        #     f.write(jb_city+'\n')
        #     f.write(jb_exp+'\n')
        #     f.write(jb_study+'\n')
        #     f.write(jb_type+'\n')
        #     # f.write(jb_msg+'\n')
        #     f.write(jb_com+'\n')
        #     f.write('-------------------')
    browser.quit()

@click.group()
def cli():
    pass

@cli.command(help='find job list')
def a():
    for ji in jbs:
        for jc in citys:
            try:
                get_lagouwang(ji,jc)
            except Exception:
                raise Exception

@cli.command(help='find job msg')
def b():
    get_jobinfo()


if __name__=='__main__':
    cli()
