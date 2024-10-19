from openai import OpenAI
import sys

class OpenAIClient:
    def __init__(self, api_key, model, logger):
        self.logger = logger
        self.llmModel = model
        self.client = OpenAI(api_key=api_key)
        self.logger.debug(self.__dict__)

    def Chat(self, systemInstruction, userPrompt):
        try:
        #self.logger.debug(userPrompt)
            completion = self.client.chat.completions.create(
                model=self.llmModel,
                messages=[
                    {"role": "system", "content": systemInstruction},
                    {
                        "role": "user",
                        "content": userPrompt
                    }
                ]
            )        
            #print(completion.choices[0].message.content)

            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: userPrompt: [{userPrompt}] : {e}')
            raise

    def GeneralChat(self, userPrompt):
        try:
        #self.logger.debug(userPrompt)
            completion = self.client.chat.completions.create(
                model=self.llmModel,
                messages=[        
                    {"role": "system", "content": "Your are helpful AI assistant Gideon from flash."},           
                    {
                        "role": "user",
                        "content": userPrompt
                    }
                ]
            )        
            #print(completion.choices[0].message.content)

            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: userPrompt: [{userPrompt}] : {e}')
            raise