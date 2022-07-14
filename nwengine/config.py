from nwengine.error import EngineError

class InvalidConfig(EngineError):
    def __init__(self, msg, *args, **kwargs):
        prefix = "Invalid Configuration: "
        super().__init__(prefix + msg, *args, **kwargs)

class Config:
    def __init__(self, params: dict=None):
        if params:
            if not params.internal_db_addr:
                self.internal_db_addr = "localhost"
            else:
                self.internal_db_addr = params.internal_db_addr
            if not params.internal_db_port:
                self.internal_db_port = 27017
            else:
                if not isinstance(params.internal_db_port, int):
                    raise InvalidConfig("internal_db_port expected int")
                self.internal_db_port = params.internal_db_addr
            if not params.export_raw:
                self.export_raw = False
            else:
                self.export_raw = True
            if not params.out_db_addr:
                self.out_db_addr = self.internal_db_addr
            else: 
                self.out_db_addr = params.out_db_addr
            if not params.out_db_port:
                self.out_db_port = self.internal_db_port
            else:
                if not isinstance(params.out_db_port, int):
                    raise InvalidConfig("out_db_port expected int")
                self.out_db_port = params.out_db_addr
            if not params.out_db_name:
                self.out_db_name = "nodewatts"
            else:
                self.out_db_name = params.out_db_name
            if not params.profile_id:
                raise InvalidConfig("profile_id not provided")
            else:
                self.profile_id = params.profile_id
            if not params.report_name:
                raise InvalidConfig("report_name must be provided")
            else:
                self.report_name = params.report_name
            if not params.sensor_start:
                raise InvalidConfig("sensor_start must be provided")
            else:
                self.sensor_start = params.sensor_start
            if not params.sensor_end:
                raise InvalidConfig("sensor_end must be provided")
            else:
                self.sensor_end = params.sensor_end
            if not params.verbose:
                self.verbose = False
            else:
                self.verbose = params.verbose
            