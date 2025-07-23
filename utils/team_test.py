import asyncio

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Create the agents.
model_client = OpenAIChatCompletionClient(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-f95b28efff5f434db7a3be957504b586",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": False
    }
)
async def main():
    assistant = AssistantAgent("assistant", model_client=model_client)
    user_proxy = UserProxyAgent("user_proxy", input_func=input)  # Use input() to get user input from console.

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("APPROVE")

    # Create the team.
    # team = RoundRobinGroupChat([assistant, user_proxy], termination_condition=termination)
    team = RoundRobinGroupChat([assistant], max_turns=2)

    # Run the conversation and stream to the console.
    stream = team.run_stream(task="Write a 4-line poem about the ocean.")
# Use asyncio.run(...) when running in a script.
    await Console(stream)
    await model_client.close()

if __name__ == '__main__':
    asyncio.run(main())
