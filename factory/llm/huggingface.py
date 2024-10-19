from huggingface_hub import InferenceClient
import sys

class HfInferenceApiClient:
	def __init__(self, llmModel, hfToken, logger):
		self.logger = logger
		self.llmModel = llmModel or "microsoft/Phi-3.5-mini-instruct" #default model
		self.client = InferenceClient(self.llmModel,token=hfToken)
		self.logger.debug(self.__dict__)

	def Query(self, userPrompt, maxTokens)->str:
		try:
			#userPrompt = instruction.replace("[prompttext]", text)
			#chatMsg = f"{prompt}"
			all_messages=""
			for message in self.client.chat_completion(
				messages=[{"role": "user", "content": userPrompt}], max_tokens=maxTokens, stream=True):
				all_messages += message.choices[0].delta.content
			#print(all_messages)
			return all_messages
		except Exception as e:
			self.logger.error(f'{sys._getframe().f_code.co_name}: userPrompt: [{userPrompt}] : {e}')
			raise
			
