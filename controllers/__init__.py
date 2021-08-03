from controllers.TestController import TestController
from controllers.HealthCheckController import HealthCheckController
from controllers.PersonController import PersonController
from controllers.RoleController import RoleController
from controllers.StatusController import StatusController
from controllers.UserController import UserController
from controllers.NotificationController import NotificationController
from controllers.DeviceController import DeviceController
from controllers.FileLocalController import FileLocalController
from controllers.FileS3Controller import FileS3Controller
from controllers.PasswordRecoveryController import PasswordRecoveryController
from controllers.ConfirmEmailController import ConfirmEmailController
from controllers.SessionController import SessionController

testController = TestController()
healthcheckController = HealthCheckController()
personController = PersonController()
roleController = RoleController()
statusController = StatusController()
userController = UserController()
notificationController = NotificationController()
deviceController = DeviceController()
filelocalController = FileLocalController()
files3Controller = FileS3Controller()
passwordrecoveryController = PasswordRecoveryController()
confirmemailController = ConfirmEmailController()
sessionController = SessionController()
