import MVAgentLauncher
import sys
from MVAgentLaunchert import MVAgentLauncher
def AgentLauncher():
    # print("Arnon")
    # print(sys.argv)
    MVAgentLauncher.main(sys.argv[1:])
    MVAgentLauncher.stop_test_processing(True)