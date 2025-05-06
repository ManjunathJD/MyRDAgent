"""
We have implemented a basic version of litellm.
Not all features in the interface are included.
Therefore, the advanced tests will be placed in a separate file for easier testing of litellm.
Python 3.13 compatible: Added typing hints, fixed assert usage
"""

import json
import random
import unittest

from rdagent.oai.llm_utils import APIBackend
from typing import List, Any, Tuple

def _worker(system_prompt: str, user_prompt: str) -> Any:
    api = APIBackend()
    return api.build_messages_and_create_chat_completion(
        system_prompt = system_prompt,
        user_prompt=user_prompt,
    )


class TestAdvanced(unittest.TestCase):

    def test_add(self) -> None:
        self.assertTrue(True)
        
    def test_chat_cache_multiprocess(self) -> None:
        """
        Tests:
        - Multi process, ask same question, enable cache
            - 2 pass
            - cache is not missed & same question get different answer.
        """
        from rdagent.core.utils import LLM_CACHE_SEED_GEN, multiprocessing_wrapper
        from rdagent.oai.llm_conf import LLM_SETTINGS
        
        system_prompt = "You are a helpful assistant."
        user_prompt = f"Give me {2} random country names, list {2} cities in each country, and introduce them"

        origin_value = (
            LLM_SETTINGS.use_auto_chat_cache_seed_gen,
            LLM_SETTINGS.use_chat_cache,
            LLM_SETTINGS.dump_chat_cache,
        )

        LLM_SETTINGS.use_chat_cache = True
        LLM_SETTINGS.dump_chat_cache = True

        LLM_SETTINGS.use_auto_chat_cache_seed_gen = True

        func_calls: List[Tuple[Any, Tuple[str, str]]] = [(_worker, (system_prompt, user_prompt)) for _ in range(4)]

        LLM_CACHE_SEED_GEN.set_seed(10)
        responses1: List[Any] = multiprocessing_wrapper(func_calls, n=4)
        LLM_CACHE_SEED_GEN.set_seed(20)
        responses2: List[Any] = multiprocessing_wrapper(func_calls, n=4)
        LLM_CACHE_SEED_GEN.set_seed(10)
        responses3: List[Any] = multiprocessing_wrapper(func_calls, n=4)

        # Reset, for other tests
        (
            LLM_SETTINGS.use_auto_chat_cache_seed_gen,
            LLM_SETTINGS.use_chat_cache,
            LLM_SETTINGS.dump_chat_cache,
        ) = origin_value        
        
        for i in range(len(func_calls)):
            self.assertNotEqual(responses1[i], responses2[i])
            self.assertEqual(responses1[i], responses3[i])
            
            
            for j in range(i + 1, len(func_calls)):
                assert (
                    responses1[i] != responses1[j] and responses2[i] != responses2[j]
                ), "Same question should get different response when use_auto_chat_cache_seed_gen=True"

    def test_chat_multi_round(self) -> None:
        system_prompt = "You are a helpful assistant."
        fruit_name: str = random.SystemRandom().choice(["apple", "banana", "orange", "grape", "watermelon"])
        user_prompt_1 = (
            f"I will tell you a name of fruit, please remember them and tell me later. "
            f"The name is {fruit_name}. Once you remember it, please answer OK."
        )
        user_prompt_2 = "What is the name of the fruit I told you before?"

        session: Any = APIBackend().build_chat_session(session_system_prompt=system_prompt)

        response_1: Any = session.build_chat_completion(user_prompt=user_prompt_1)
        self.assertIsNotNone(response_1)
        self.assertIn("ok", response_1.lower())

        response2: Any = session.build_chat_completion(user_prompt=user_prompt_2)
        self.assertIsNotNone(response2)


    def test_chat_cache(self) -> None:
        """
        Tests:
        - Single process, ask same question, enable cache
            - 2 pass
            - cache is not missed & same question get different answer.
        """
        from rdagent.core.utils import LLM_CACHE_SEED_GEN
        from rdagent.oai.llm_conf import LLM_SETTINGS

        system_prompt = "You are a helpful assistant."
        user_prompt = f"Give me {2} random country names, list {2} cities in each country, and introduce them"

        origin_value = (
            LLM_SETTINGS.use_auto_chat_cache_seed_gen,
            LLM_SETTINGS.use_chat_cache,
            LLM_SETTINGS.dump_chat_cache,
        )

        LLM_SETTINGS.use_chat_cache = True
        LLM_SETTINGS.dump_chat_cache = True

        LLM_SETTINGS.use_auto_chat_cache_seed_gen = True

        api_backend: APIBackend = APIBackend()

        LLM_CACHE_SEED_GEN.set_seed(10)
        response1: Any = api_backend.build_messages_and_create_chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        response2: Any = api_backend.build_messages_and_create_chat_completion(system_prompt=system_prompt, user_prompt=user_prompt,)

        LLM_CACHE_SEED_GEN.set_seed(20)
        response3: Any = api_backend.build_messages_and_create_chat_completion(system_prompt=system_prompt, user_prompt=user_prompt,)
        response4: Any = api_backend.build_messages_and_create_chat_completion(system_prompt=system_prompt, user_prompt=user_prompt,)

        LLM_CACHE_SEED_GEN.set_seed(10)
        response5: Any = api_backend.build_messages_and_create_chat_completion(system_prompt=system_prompt, user_prompt=user_prompt,)
        response6: Any = api_backend.build_messages_and_create_chat_completion(system_prompt=system_prompt, user_prompt=user_prompt,)

        # Reset, for other tests
        (
            LLM_SETTINGS.use_auto_chat_cache_seed_gen,
            LLM_SETTINGS.use_chat_cache,
            LLM_SETTINGS.dump_chat_cache,
        ) = origin_value        

        assert (
            response1 != response3 and response2 != response4
        ), "Responses sequence should be determined by 'init_chat_cache_seed'"
        assert (
            response1 == response5 and response2 == response6
        ), "Responses sequence should be determined by 'init_chat_cache_seed'"
        assert (
            response1 != response2 and response3 != response4 and response5 != response6
        ), "Same question should get different response when use_auto_chat_cache_seed_gen=True"


if __name__ == "__main__":
    unittest.main()
