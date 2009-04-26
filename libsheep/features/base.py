from libsheep.features import Feature
from libsheep.protocol import Context, Command
from libsheep.parameters import *

class BASE(Feature):
    def enable(self):
        """Register BASE commands."""
        STA.register()
        SUP.register()
        SID.register()
        INF.register()
        MSG.register()
        SCH.register()
        RES.register()
        CTM.register()
        RCM.register()
        GPA.register()
        PAS.register()
        QUI.register()
        GET.register()
        GFI.register()
        SND.register()

# BASE messages.

class STA(Command):
    """Status message."""
    severity = Parameter(0)[0]
    error_code = Parameter(0)[1:3]
    description = Parameter(1)
    
    def encode(self):
        yield '%s%s' % (self.severity, self.error_code)
        yield self.description

class SUP(Command):
    """Feature support message."""
    add_features = Parameter('AD', Set)
    remove_features = Parameter('RM', Set)

class SID(Command):
    """Session ID message."""
    session_id = Parameter(0, Base32)

class INF(Command):
    """Info message."""
    client_cid = Parameter('ID', Base32)
    client_pid = Parameter('PD', Base32)
    ipv4_address = Parameter('I4')
    ipv6_address = Parameter('I6')
    udpv4_port = Parameter('U4', Integer)
    udpv6_port = Parameter('U6', Integer)
    share_size = Parameter('SS', Integer)
    shared_files = Parameter('SF', Integer)
    client_version = Parameter('VE')
    upload_speed = Parameter('US', Integer)
    download_speed = Parameter('DS', Integer)
    slots = Parameter('SL', Integer)
    auto_slot_speed = Parameter('AS', Integer)
    auto_slot_max = Parameter('AM', Integer)
    email = Parameter('EM')
    nickname = Parameter('NI')
    description = Parameter('DE')
    hubs_normal = Parameter('HN', Integer)
    hubs_registered = Parameter('HR', Integer)
    hubs_operator = Parameter('HO', Integer)
    token = Parameter('TO')
    client_type = Parameter('CT', BitField(
        ['BOT', 'REGISTERED', 'OPERATOR', 'SUPERUSER', 'HUB_OWNER', 'HUB']
    ))
    away_status = Parameter('AW', Integer)
    features = Parameter('SU', Delimited(','))
    referrer_url = Parameter('RF')

class MSG(Command):
    """Private message message."""
    text = Parameter(0)
    group_sid = Parameter('PM', Base32)
    is_action = Parameter('ME', Boolean, default=False)

class SCH(Command):
    """Search message."""
    include = Parameter('AN')
    exclude = Parameter('NO')
    extension = Parameter('EX')
    bytes_lower = Parameter('LE', Integer)
    bytes_upper = Parameter('GE', Integer)
    bytes_exact = Parameter('EQ', Integer)
    token = Parameter('TO')
    file_type = Parameter('TY')

class RES(Command):
    """Search result message."""
    filename = Parameter('FN')
    size = Parameter('SI', Integer)
    slots = Parameter('SL', Integer)
    token = Parameter('TO')
    
class CTM(Command):
    """Connect-to-me message."""
    protocol = Parameter(0)
    port = Parameter(1, Integer)
    token = Parameter(2)

class RCM(Command):
    """Reverse connect-to-me message."""
    protocol = Parameter(0)
    token = Parameter(0)

class GPA(Command):
    """Get password message."""
    data = Parameter(0, Base32)

class PAS(Command):
    """Password message."""
    password = Parameter(0, Base32)

class QUI(Command):
    """Quit message."""
    client_id = Parameter(0, Base32)
    initiator_sid = Parameter('ID', Base32)
    time_left = Parameter('TL', Integer)
    message = Parameter('MS')
    redirect_url = Parameter('RD')
    disconnect = Parameter('DI', Flag)

class GET(Command):
    """Request file message."""
    type = Parameter(0)
    identifier = Parameter(1)
    start_pos = Parameter(2, Integer)
    bytes = Parameter(3, Integer)
    recursive = Parameter('RE', Boolean, default=False)

class GFI(Command):
    """Get file information message."""
    type = Parameter(0)
    identifier = Parameter(1)

class SND(Command):
    """Transfer file message."""
    type = Parameter(0)
    identifier = Parameter(1)
    start_pos = Parameter(2, Integer)
    bytes = Parameter(3, Integer)
