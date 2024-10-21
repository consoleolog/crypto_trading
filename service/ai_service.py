import json

from pandas import DataFrame

from config import OPENAI_API_KEY

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langchain.schema import BaseOutputParser

from logger import get_logger


class JsonOutputParser(BaseOutputParser):
    def parse(self, text: str):
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)

class LLmService:
    def __init__(self, ticker: str):
        self.output_parser = JsonOutputParser()
        self.TICKER = ticker
        self.log = get_logger(ticker)

        self.model = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model='gpt-4o-mini'
        )

    def trading(self, inputs:dict[str, DataFrame])->dict[str, str]:

        data = inputs["data"]
        data.drop(["close",
                   "ema_short","ema_middle","ema_long",
                   "macd_short_slope","macd_middle_slope","macd_long_slope"], axis=1, inplace=True)
        data.dropna(inplace=True)

        template = ChatPromptTemplate.from_messages([
            ("system",
             """
            너는 암호화폐 전문가야 매수/ 매도 조건을 따라 매수 : BUY 할지 매도 : SELL 할지 , HOLD 할지 결정해줘
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

            답변을 JSON 형식으로 출력해줘.

          Example output:
            ```json
            {{
                "reason": "이유를 말할 때 정확한 숫자 수치를 포함해줘",
                "result": "BUY"
            }}
            ```
            ```json
            {{
                "reason": "이유를 말할 때 정확한 숫자 수치를 포함해줘",
                "result": "SELL"
            }}
            ```
            ```json
            {{
                "reason": "이유를 말할 때 정확한 숫자 수치를 포함해줘",
                "result": "HOLD"
            }}
            ```

            분석할 데이터 : {data}    
        """)
        ])

        chain = template | self.model | self.output_parser
        result = chain.invoke({
            "data": data
        })
        self.log.debug(f"""
        ==============================================================================================================================      
          ** 매매 분석 **
          $$ {result['reason']}
        ==============================================================================================================================  
        """)
        return result