from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.adimage import AdImage
from facebookads.adobjects.campaign import Campaign
from facebookads.adobjects.adset import AdSet
from facebookads.adobjects.adcreative import AdCreative
from facebookads.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec
from facebookads.adobjects.adcreativelinkdata import AdCreativeLinkData
from facebookads.adobjects.adcreativetextdata import AdCreativeTextData
from facebookads.adobjects.adcreativephotodata import AdCreativePhotoData
from facebookads.adobjects.ad import Ad
from facebookads.adobjects.adpreview import AdPreview
from facebookads.adobjects.targeting import Targeting
from facebookads.adobjects.targetingsearch import TargetingSearch
from facebookads.adobjects.targetinggeolocationcustomlocation import TargetingGeoLocationCustomLocation
from facebookads.adobjects.adimage import AdImage
from facebookads import adobjects

import datetime

import credentials

from scrape_live_booker import scrape_info, scrape_image, scrape_with_requests_only
from image_path import download_image_from_url



my_app_id = credentials.credentials['app_id']
my_app_secret = credentials.credentials['app_secret']
my_access_token = credentials.credentials['access_token']

page_id_facebook = "YourPageID"
account_publicitaire  = "act_accountNumberHere"

my_account = AdAccount(account_publicitaire)
FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)


daily_budget = 1000000 #10 000€ par jour :p
print('Vous voulez créer une Facebook Ads pour votre service.')
print('                                                                ')


url = input("Entrez l'URL de la fiche produit:  ")

ville, pays, variable, date = scrape_with_requests_only(url)




is_target_city = input("Voulez vous cibler une ville plutôt qu'un pays ? (y/n)")

if 'y' in is_target_city.lower():
    is_target_city = True
else:
    is_target_city = False


if is_target_city:
    target_location = input('Entrez le nom de la ville que vous voulez cibler:   ')
else:
    target_location = input("Entrez le nom du pays que vous voulez cibler:   ")



try:
    image_url = scrape_image(url)
    print(image_url)
    image_path = download_image_from_url(image_url)
    print(image_path)
except:
    image_path = input("Entrez le path de l'image utilisée pour la publicité: ")


campaign = Campaign(parent_id = account_publicitaire)


campaign[Campaign.Field.name] = variable + " " + pays
campaign[Campaign.Field.configured_status] = Campaign.Status.active
campaign[Campaign.Field.objective] = Campaign.Objective.conversions

campaign.remote_create()
campaign = campaign[AdSet.Field.id]

ad_set =  AdSet(parent_id = account_publicitaire)
ad_set[AdSet.Field.campaign_id] = campaign
ad_set[AdSet.Field.name] = variable + ' ' + target_location
ad_set[AdSet.Field.optimization_goal] = AdSet.OptimizationGoal.offsite_conversions
ad_set[AdSet.Field.destination_type] = "WEBSITE"
ad_set[AdSet.Field.promoted_object] = {
    'pixel_id': 'YOURPIXELID',
    'custom_event_type':'PURCHASE',
}
ad_set[AdSet.Field.billing_event] = AdSet.BillingEvent.impressions
ad_set[AdSet.Field.is_autobid] = True
ad_set[AdSet.Field.daily_budget] = daily_budget
ad_set[AdSet.Field.start_time]=datetime.datetime.now()
targeting = {}

params_location = {
    'q': target_location,
    'type':'adgeolocation'
}
location = TargetingSearch.search(params=params_location)

if is_target_city:
    targeting[Targeting.Field.geo_locations] = {
     "cities":
         { "key": location[0]['key']},
     }
else:
    targeting[Targeting.Field.geo_locations] = {
    "countries": location[0]['country_code'].split()
    }

params_interest = {
    'q':variable,
    'type':'adinterest',
    }
interest = TargetingSearch.search(params=params_interest)
interest_id = interest[0]['id']
interest_name = interest[0]['name']

targeting[Targeting.Field.interests] = [
          {
            'id':interest_id,
            'name':interest_name,
            }
           ]
targeting[Targeting.Field.publisher_platforms] = ['facebook','instagram','messenger']
targeting[Targeting.Field.facebook_positions] = ['feed']
targeting[Targeting.Field.instagram_positions] = ['stream']
targeting[Targeting.Field.messenger_positions] = ['messenger_home']

ad_set[AdSet.Field.targeting] = targeting

ad_set.remote_create()


img = AdImage(parent_id = account_publicitaire)
img[AdImage.Field.filename] = image_path
img.remote_create()
image_hash = img.get_hash()




link_data = AdCreativeLinkData()
link_data[AdCreativeLinkData.Field.link] = url
link_data[AdCreativeLinkData.Field.image_hash] = image_hash




link_data[AdCreativeLinkData.Field.message] = "Le texte de votre publicité ici."
link_data[AdCreativeLinkData.Field.description] = "Le petit message en dessous du titre de la publicité."
link_data[AdCreativeLinkData.Field.name] = "Le titre de votre publicité"
link_data[AdCreativeLinkData.Field.caption] = 'votredomaine.fr'


call_to_action = {
    'type': 'LEARN_MORE',
    'value': {
        'link': url,
    },
}
link_data[AdCreativeLinkData.Field.call_to_action] = call_to_action

object_story_spec = AdCreativeObjectStorySpec()
object_story_spec[AdCreativeObjectStorySpec.Field.page_id] = page_id_facebook
object_story_spec[AdCreativeObjectStorySpec.Field.link_data] = link_data



creative = AdCreative(parent_id = account_publicitaire)
creative[AdCreative.Field.url_tags] = "vos balises utm ici"
creative[AdCreative.Field.object_story_spec] = object_story_spec
creative.remote_create()


ad = Ad(parent_id = account_publicitaire)
ad[Ad.Field.name] = variable + ' Ad'
ad[Ad.Field.adset_id] = ad_set[AdSet.Field.id]
ad[Ad.Field.tracking_specs] ={
            'action.type':'offsite_conversion',
            'fb_pixel': YOURFACEBOOKPIXEL
            }
ad[Ad.Field.creative] = {
    'creative_id': creative['id'],
}
ad.remote_create(params={
    'status':Ad.Status.active,
})



print('Campaign successfully created, congrats!')
