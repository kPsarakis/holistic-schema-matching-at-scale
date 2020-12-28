from os import environ
from redis import Redis

redis_host = environ['REDIS_HOST']
redis_port = environ['REDIS_PORT']
redis_pwd = environ['REDIS_PASSWORD']

match_result_db: Redis = Redis(host=redis_host, 
                               port=redis_port, 
                               password=redis_pwd,
                               db=1)

insertion_order_db: Redis = Redis(host=redis_host, 
                                  port=redis_port, 
                                  password=redis_pwd,
                                  charset="utf-8", 
                                  decode_responses=True, 
                                  db=2)

verified_match_db: Redis = Redis(host=redis_host, 
                                 port=redis_port, 
                                 password=redis_pwd,
                                 charset="utf-8", 
                                 decode_responses=True, 
                                 db=3)

runtime_db: Redis = Redis(host=redis_host, 
                          port=redis_port, 
                          password=redis_pwd,
                          charset="utf-8", 
                          decode_responses=True, 
                          db=4)

task_result_db: Redis = Redis(host=redis_host, 
                              port=redis_port, 
                              password=redis_pwd,
                              db=5)
