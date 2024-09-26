

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
                        5. 세개의 macd의 기울기가 우상향일 때
                        
            매도 조건 :  1. 이동 평균선이 어느정도의 기간 동안 상승한 뒤 횡보하거나 약간 하락 기조로 전환된 시기에 가격이 그 이동 평균선을 위에서 아래로 뚜렷하게 교차했을 때
                        2. 이동 평균선이 지속적으로 하락하는 시기에 가격이 이동 평균선을 왼쪽에서 오른쪽으로 교차했을때
                        3. 가격이 하락 기조의 이동 평균선보다 아래에 있고, 그 후 이동 평균선을 향해 접근 하지만 이동 평균선과 교차하지 않고 다시 하락하기 시작했을 때,
                        4. 가격이 상승 기조의 이동 평균선 보다 위에 있고, 이동 평균선으로 부터 크게 괴리되어 있을 때
                        5. 세개의 macd의 기울기가 우하향일 때  
                        
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

def compare_with_mine(market_price, my_price, current_market_price):
    template = ChatPromptTemplate.from_messages([
        ("system",""" 수수료가 0.05% 일 때 현재 내가 가지고있는 암호화폐를 팔면 손실 : LOSS 이 발생하는지 이익 : PROFIT 이 발생하는지 알려줘
            이익이 10원 이하면 HOLD 를 출력해줘
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
            
            {{{{
            reason: "이유를 말할때에는 정확한 숫자의 수치를 포함해서 말해줘 "
            }},
            {{
                result: "HOLD"
            }}}}
        """),
        ("ai","""
            답변을 할 때는 json 형태로 답변해줘
            이유를 말할 때에는 정확한 숫자의 수치를 포함해서 말해줘  
            example output :
            {{{{
            reason: "구매할 때의 암호화폐 가격은 84,688,000원이었고, 현재 시장의 암호화폐 가격은 84,634,000원이므로 손실이 발생합니다. 손실액은 (84,688,000 - 84,634,000) * (6003 / 84,688,000) = 3,241.44원입니다. 이 손실액은 10원 이상입니다."
            }},
            {{
                result: "LOSS"
            }}}}
            
            {{{{
            reason: "구매할 때의 암호화폐 가격은 84549000.0원이었고, 6010원을 매수했으므로 매수한 암호화폐의 양은 6010 / 84549000.0 = 0.0000711 BTC입니다. 현재 시장 가격은 84576000.0원이므로 현재 가치(0.0000711 BTC * 84576000.0) = 6011.68원이 됩니다. 매수 가격보다 현재 가치가 더 높기 때문에 이익이 발생합니다. "
            }},
            {{
                result: "PROFIT"
            }}}}
            
            {{{{
            reason: "구매했을 때의 가격은 84688000.0원이었고, 현재 가격은 84622000.0원이므로 손실이 발생했습니다. 손실 금액은 (84688000.0 - 84622000.0) * (6003 / 84688000.0) = 약 4.7원입니다. 손실이 10원 이하이므로 HOLD합니다. "
            }},
            {{
                result: "HOLD"
            }}}}
        """),
        ("human",""" 구매할때의 암호화폐 가격 : {marketPrice} ( {myPrice}원 만큼 매수) 
                         
                     현재 시장의 암호화폐 가격 : {currentMarketPrice}
                     """)
    ])
    chain = template | model | SimpleJsonOutputParser()
    try:
        result = chain.invoke({
            "marketPrice": market_price,
            "myPrice":my_price,
            "currentMarketPrice": current_market_price
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
            "marketPrice": market_price,
            "myPrice": my_price,
            "currentMarketPrice": current_market_price
        })