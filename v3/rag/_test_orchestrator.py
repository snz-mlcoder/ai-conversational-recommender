from rag.workflow.orchestrator import handle_user_message
from rag.workflow.schemas import SearchMemory


def run_test(message, memory):
    reply, new_memory, debug = handle_user_message(message, memory)
    print("USER:", message)
    print("BOT :", reply)
    print("MEM :", new_memory)
    print("DBG :", debug)
    print("-" * 40)
    return new_memory


if __name__ == "__main__":
    memory = SearchMemory()

    memory = run_test("Mi serve qualcosa per servire a tavola", memory)
    memory = run_test("piatto", memory)
    memory = run_test("bianco", memory)
