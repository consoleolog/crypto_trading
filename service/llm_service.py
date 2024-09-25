

from config import *

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import SimpleJsonOutputParser, JsonOutputParser

from logger import log

model = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model='gpt-4o-mini'
)


def decision_buy_or_sell(data):
    template = ChatPromptTemplate.from_messages(
        [
            ("system","""
            너는 암호화폐 전문가야 매수/ 매도 조건을 따라 매수 : BUY 할지 매도 : SELL 할지 결정해줘
            
            매수 조건 :  1. 이동 평균선이 어느정도의 시간 동안 하락한 뒤 횡보하거나 약간 상승 기조로 전환된 시기에 가격이 그 이동 평균선을 아래서 위로 뚜렷하게 교차했을때
                        2. 이동 평균선이 지속적으로 상승하는 시기에 가격이 이동 평균선을 왼쪽에서 오른쪽으로 교차했을 때
                        3. 가격이 상승 기조의 이동 평균선 보다 위에 있고, 그 후 이동 평균선을 향해 접근하지만 이동 평균선과 교차하지 않고 다시 상승하기 시작할때
                        4. 가격이 하락기조의 이동 평균선보다 아래에 있고, 이동 평균선으로부터 그게 괴리되었을때   
                        5. 세개의 macd 가 우상향일 때
                        
            매도 조건 :  1. 이동 평균선이 어느정도의 기간 동안 상승한 뒤 횡보하거나 약간 하락 기조로 전환된 시기에 가격이 그 이동 평균선을 위에서 아래로 뚜렷하게 교차했을 때
                        2. 이동 평균선이 지속적으로 하락하는 시기에 가격이 이동 평균선을 왼쪽에서 오른쪽으로 교차했을때
                        3. 가격이 하락 기조의 이동 평균선보다 아래에 있고, 그 후 이동 평균선을 향해 접근 하지만 이동 평균선과 교차하지 않고 다시 하락하기 시작했을 때,
                        4. 가격이 상승 기조의 이동 평균선 보다 위에 있고, 이동 평균선으로 부터 크게 괴리되어 있을 때
                        5. 세개의 macd가 우하향일 때  
                        
            example output :
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "SELL"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "BUY"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "HOLD"
            }}}}
            """),
            ("ai","""
            답변할때는 json 형태로 반환
            example output :
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "SELL"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "BUY"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "HOLD"
            }}}}
            """),
            ("human","{data}")
        ]
    )
    chain = template | model | SimpleJsonOutputParser()
    try:
        result = chain.invoke({
            "data":data
        })
        log.debug(f"""
        ==============================================================================================================================      
        ##  ** 매매 분석 **
        ## 
        ##  {result['reason']}
        ##
        ==============================================================================================================================  
        """)
        return result
    except Exception as e:
        log.error(e)
        error_chain = template | model | JsonOutputParser()
        return error_chain.invoke({
            "data":data
        })

def compare_with_mine(my_balance, market_balance):
    template = ChatPromptTemplate.from_messages([
        ("system",""" 수수료가 0.05% 일 때 현재 내가 가지고있는 암호화폐를 팔면 손실 : LOSS 이 발생하는지 이익 : PROFIT 이 발생하는지 알려줘
            이유를 말할 때에는 정확한 숫자의 수치를 포함해서 말해줘  
            example output :
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "NOT_SELL"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "SELL"
            }}}}
        """),
        ("ai","""
            답변을 할 때는 json 형태로 답변해줘
            이유를 말할 때에는 정확한 숫자의 수치를 포함해서 말해줘  
            example output :
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "LOSS"
            }}}}
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "PROFIT"
            }}}}
        """),
        ("human",""" 구매할때의 암호화폐 가격 : {myBalance} (6010원 만큼 매수) 
                         
                     현재 시장의 암호화폐 가격 : {marketBalance}
                     """)
    ])
    chain = template | model | SimpleJsonOutputParser()
    try:
        result = chain.invoke({
            "myBalance": my_balance,
            "marketBalance": market_balance
        })
        log.debug(f"""
        ==============================================================================================================================
        ##  ** 내 가격과 현재 시장 가격 비교 **
        ## 
        ##  {result['reason']}
        ##
        ==============================================================================================================================
        """)
        return result
    except Exception as e:
        log.error(e)
        error_chain = template | model | JsonOutputParser()
        return error_chain.invoke({
            "myBalance": my_balance,
            "marketBalance": market_balance
        })