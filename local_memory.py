import constants as C
# {user_id0:{channel_id0,channel_id1...}, user_id1...}, where user_id* - superuser, which use cmd

cmd_channels = {}    # for !mute, !*deny, !purge
rep_channels = {}    # for !say and reports for *deny commands
torpor_users = {}
silence_users = {}
cmd_server = {}

# set(id0, id1, ...)
mute_channels = set()
mute_light_channels = set()
test_channels = set()
ignore_users = set()
emoji_users = set()

game = False    # type: str or bool
silence_ans = {}
embrace_first = []
embrace_not = set()
t_start = None # type: C.Types.Datetime
t_finish = None # type: C.Types.Datetime
t_work = None   # type: C.Types.Datetime
last_vtm_msg = None # type: int
debug = False
