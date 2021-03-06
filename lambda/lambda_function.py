import logging
import json
import ask_sdk_core.utils as ask_utils
import math
from word2number import w2n

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.dispatch_components import AbstractResponseInterceptor
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# read mock data
with open('car_data.json', 'r') as myfile:
    jsonData = myfile.read()

all_cars = json.loads(jsonData)

with open('default_cars_data.json', 'r') as myfile:
    carsjsonData = myfile.read()

default_cars = json.loads(carsjsonData)

class GetRecommendationAPIHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.request_util.get_request_type(handler_input) == 'Dialog.API.Invoked' and handler_input.request_envelope.request.api_request.name == 'getRecommendation'


    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        api_request = handler_input.request_envelope.request.api_request
        
        recommendationResult = {}
        # recommendationResult['name'] = "optimus prime is the right car for you"
        filtered_cars = []

        brand = resolveEntity(api_request.slots, "brand")
        budget = resolveEntity(api_request.slots, "budget")
        fuelefficiency = resolveEntity(api_request.slots, "fuelefficiency")
        reliable = resolveEntity(api_request.slots, "reliable")
        rugged = resolveEntity(api_request.slots, "rugged")
        spacious = resolveEntity(api_request.slots, "spacious")

        if budget != None:
            # print(budget, 'budget')
            if budget == 'cheap':
                #cheap is below $20k
                # print('inside cheap')
                for car in all_cars:
                    if not math.isnan(float(car['MSRP'])) and int(float(car['MSRP'])) < 20:
                        filtered_cars.append(car)
                print(len(filtered_cars), 'after filtering by cheap')
            elif budget == 'luxury':
                #print('inside luxury')
                #luxury is above $80k
                for car in all_cars:
                    if not math.isnan(float(car['MSRP'])) and int(float(car['MSRP'])) > 80:
                        filtered_cars.append(car)
                print(len(filtered_cars), 'after filtering by luxury')
            elif budget == 'midrange':
                #print('inside midrange')
                #midrange is 21k to 79k
                for car in all_cars:
                    if not math.isnan(float(car['MSRP'])) and int(float(car['MSRP'])) >= 21 and int(float(car['MSRP'])) < 79:
                        filtered_cars.append(car)
                print(len(filtered_cars), 'after filtering by midrange')
            else:
                print('not filtering for budget')
                filtered_cars = all_cars
        
        if brand != None:
            print(brand, 'brand')
            if len(filtered_cars) > 0 and brand.lower() != 'no preference':
                filtered_cars = [car for car in filtered_cars if car['Make'].lower() == brand.lower()]
                print(len(filtered_cars), 'after brand filtering')
                    

        if rugged != None:
            #Body style of truck, SUV && Drivetrain of AWD && horsrpower 350 and above
            print(rugged, 'printing value of rugged')
            if rugged != 'rugged' and len(filtered_cars) > 0:
                print('inside not rugged')
                filtered_cars = [car for car in filtered_cars if car['Drivetrain'] == 'RWD' or car['Drivetrain'] == 'FWD']
                filtered_cars = [car for car in filtered_cars if int(car['Horsepower']) < 350]
                print(len(filtered_cars), 'after filtering by not rugged')
            elif rugged == 'rugged' and len(filtered_cars) > 0:
                print('inside rugged')
                filtered_cars = [car for car in filtered_cars if car['Drivetrain'] == 'AWD']
                filtered_cars = [car for car in filtered_cars if int(car['Horsepower']) >= 350]
                filtered_cars = [car for car in filtered_cars if car['Body Style'] == 'Pickup' or car['Body Style'] == 'SUV']
                print(len(filtered_cars), 'after filtering by rugged')
            else:
                print('filtered_cars might be zero')

        if spacious != None:
            #2-9 seats
            seats_needed = 0
            text_numbers = ['two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
            for string_number in text_numbers:
                if string_number in spacious:
                    seats_needed = w2n.word_to_num(string_number)
                    print(seats_needed)
                    if seats_needed > 0 and len(filtered_cars) > 0:
                        filtered_cars = [car for car in filtered_cars if int(car['Passenger Capacity']) == seats_needed]
            print(len(filtered_cars), 'filtered by spacious seats needed were', seats_needed)
        
        if reliable != None:
            #Year (older than 2019 not reliable)
            print(reliable, 'reliable slot type')
            if reliable == 'reliable' and len(filtered_cars) > 0:
                print('inside reliable')
                filtered_cars = [car for car in filtered_cars if int(car['Year']) >= 2019]
                print(len(filtered_cars), 'after filtering by cars year 2019 and recent')
            elif reliable != 'reliable' and len(filtered_cars) > 0:
                filtered_cars = [car for car in filtered_cars if int(car['Year']) < 2019]
                print(len(filtered_cars), 'after filtering by cars older than 2019')
            else:
                print('filtered_cars might be zero')
                
        if fuelefficiency != None:
            #Gas Mileage above 30 is efficient
            print(fuelefficiency, 'fuelefficiency slot type')
            if fuelefficiency == 'fuel efficient' and not math.isnan(float(car['Gas Mileage'])) and len(filtered_cars) > 0:
                filtered_cars = [car for car in filtered_cars if int(car['Gas Mileage']) >= 30]
            elif fuelefficiency != 'fuel efficient' and len(filtered_cars) > 0 and not math.isnan(float(car['Gas Mileage'])):
                filtered_cars = [car for car in filtered_cars if int(car['Gas Mileage']) < 30]
            else:
                print('did not filter by gas Mileage')
        
        if len(filtered_cars) == 0:
            #return some default cars if filtered cars array is empty
            filtered_cars = default_cars
            
        # response = {
        #     'apiResponse': {
        #         'cityName': cityNameWithId.name,
        #         'lowTemperature': weather['lowTemperature'],
        #         'highTemperature': weather['highTemperature']
        #     }
        # }
        
        recommendationResults = []
        recommendationResults = default_cars
        print(filtered_cars)
        recommendationResult['name'] = "Toyota Corolla 2020"
        # recommendationResult['budget'] = "12k"
        # recommendationResult['brand'] = "BMW"
        # recommendationResult['url'] = "image.com/image"

        response = buildSuccessApiResponse(recommendationResult)
        
        return response

# Formats JSON for return
# You can use the private SDK methods like "setApiResponse()", but for this template for now, we just send back
# the JSON. General request and response JSON format can be found here:
# https://developer.amazon.com/docs/custom-skills/request-and-response-json-reference.html
def buildSuccessApiResponse(returnEntity):
    return { "apiResponse": returnEntity }

# *****************************************************************************
# Generic session-ended handling logging the reason received, to help debug in error cases.
# Ends Session if there is an error 
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


# *****************************************************************************
# Resolves catalog value using Entity Resolution
def resolveEntity(resolvedEntity, slotName):
    erAuthorityResolution = resolvedEntity[slotName].resolutions.resolutions_per_authority[0]
    value = None

    if erAuthorityResolution.status.code.value == 'ER_SUCCESS_MATCH':
        try:
            value = erAuthorityResolution.values[0].value.name
        except ValueError:
            print("Oops!  That was no valid value.")
    print(value)
    return value

# The intent reflector is used for interaction model testing and debugging.
# It will simply repeat the intent the user said. You can create custom handlers
# for your intents by defining them above, then also adding them to the request
# handler chain below.
class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


# *****************************************************************************
# These simple interceptors just log the incoming and outgoing request bodies to assist in debugging.

class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        print("Request received: {}".format(
            handler_input.request_envelope.request))


class LoggingResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        print("Response generated: {}".format(response))


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.
sb = SkillBuilder()

# register request / intent handlers
sb.add_request_handler(GetRecommendationAPIHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

# register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# register interceptors
sb.add_global_request_interceptor(LoggingRequestInterceptor())
sb.add_global_response_interceptor(LoggingResponseInterceptor())

lambda_handler = sb.lambda_handler()