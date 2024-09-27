from typing import Type

from langchain_community.agent_toolkits import create_json_agent
from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, create_json_agent

from langchain.tools import BaseTool

from config import *

# CalculateProfitToolArgsSchema: 매수 및 현재 가격을 입력받는 스키마
class CalculateProfitToolArgsSchema(BaseModel):
    market_price: float = Field(
        description="매수할 당시 암호화폐의 가격"
    )
    current_market_price: float = Field(
        description="현재 암호화폐의 가격"
    )


# CalculateProfitTool: 수익 여부를 계산하는 도구 클래스
class CalculateProfitTool(BaseTool):
    name: str = "CalculateProfitTool"  # 명시적인 타입 어노테이션 추가
    description: str = """
    조건에 따라 이익 : PROFIT, 이 발생하는지 손실 : LOSS 이 발생하는지 계산하고 결과를 알려줘        
    """
    args_schema: Type[CalculateProfitToolArgsSchema] = CalculateProfitToolArgsSchema

    def _run(self, market_price, current_market_price):
        # 간단한 수익률 계산
        profit_percentage = (current_market_price - market_price) / market_price * 100
        if profit_percentage > 0:
            return {
                "reason": f"수익률: {profit_percentage:.2f}%",
                "result": "PROFIT"
            }
        elif profit_percentage < 0:
            return {
                "reason": f"손실률: {profit_percentage:.2f}%",
                "result": "LOSS"
            }
        else:
            return {
                "reason": "수익도 손실도 없습니다.",
                "result": "HOLD"
            }


# OpenAI 모델 초기화
model = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model='gpt-4o-mini'
)

# 에이전트 초기화
agent = initialize_agent(
    llm=model,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True,
    tools=[CalculateProfitTool()],
    agent_kwargs={
        "system_message": SystemMessage(
            content="""
            너는 암호화폐 전문가야 
            조건에 따라 이익 : PROFIT, 이 발생하는지 손실 : LOSS 이 발생하는지 계산하고 결과를 알려줘        

            Example output:

            ```json
            {{
                "reason": "이유를 말할 때 정확한 숫자 수치를 포함해줘",
                "result": "PROFIT"
            }}
            ```

            ```json
            {{
                "reason": "이유를 말할 때 정확한 숫자 수치를 포함해줘",
                "result": "LOSS"
            }}
            ```
            """
        )
    }
)

# 에이전트 실행
# result = agent.invoke({
#     "input": {
#         "market_price": 100000001,
#         "current_market_price": 10000000,
#     }
# })
#



tool = CalculateProfitTool()
result = tool.run(
    market_price=100000001,
    current_market_price=10000000
)

print(result)
