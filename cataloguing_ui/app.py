import json
import config
import ast

from config import my_logger, sentry_client, db, hq_db, DELHIVERY, REVERSEGAZE, OTHERS
from random import randint

from flask import Flask, jsonify, render_template, request, url_for, session, redirect, Blueprint, flash
from flask_oauthlib.client import OAuth
from flask_oauth2_login import GoogleLogin
from bson.objectid import ObjectId

from utils import update_category, get_product_tagging_details, get_vendors, get_subcategories, get_taglist, get_all_tags, inc_skip_count, add_new_subcat, get_cat_list, to_json, get_hq_cat_list, get_hq_subcat_list
from users import add_user, get_tag_count, inc_tag_count, dcr_tag_count, get_users

bp = Blueprint('bp', __name__, static_folder='static', template_folder='templates')
app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY

my_logger.info("Logging starts here")

oauth = OAuth()

############################------Google Login------####################################

app.config.update(
  GOOGLE_LOGIN_REDIRECT_SCHEME="http",
)

app.config['GOOGLE_LOGIN_CLIENT_ID'] = config.GOOGLE_CLIENT_ID
app.config['GOOGLE_LOGIN_CLIENT_SECRET'] = config.GOOGLE_CLIENT_SECRET

google_login = GoogleLogin(app)

@bp.route('/google-redirect')
def redirect_google():
    return redirect(google_login.authorization_url())

@google_login.login_success
def login_success(token, profile):
    if profile:
        domain = profile['email'].split('@')[1]

        if domain in DELHIVERY:
            profile["user_type"] = "delhivery"
        elif profile["email"] in REVERSEGAZE:
            profile["user_type"] = "reversegaze"
        elif profile["email"] in OTHERS:
            profile["user_type"] = "others"
        else:
            my_logger.error("Invalid credentials error with profile = {}".format(profile))
            flash('Invalid credentials', 'error')
            return redirect(url_for('bp.login'))

        add_user(profile)
        session['is_admin'] = False
        session['user'] = profile
        if profile['email'] in config.ADMINS:
            session['is_admin'] = True

        return redirect(url_for('bp.tag', q='tag'))
    else:
        my_logger.error("User login failed, No data returned by Google")
        flash('Login failed', 'error')
        return redirect(url_for('bp.login'))
       
@google_login.login_failure
def login_failure(e):
  return jsonify(error=str(e))

############################------Facebook Login------##################################

# facebook = oauth.remote_app('facebook',
#                             base_url='https://graph.facebook.com/',
#                             request_token_url=None,
#                             access_token_url='/oauth/access_token',
#                             authorize_url='https://www.facebook.com/dialog/oauth',
#                             consumer_key=config.FB_CONSUMER_KEY,
#                             consumer_secret=config.FB_CONSUMER_SECRET,
#                             request_token_params={'scope': 'email'})


# @bp.route('/login/fbauthorized')
# @facebook.authorized_handler
# def facebook_authorized(resp):
#     if resp is None:
#         return 'Access denied: reason=%s error=%s' % (
#             request.args['error_reason'],
#             request.args['error_description']
#         )
#     print('access_token')
#     print(resp['access_token'])
#     session['oauth_token'] = (resp['access_token'], '')

#     me = facebook.get('/me')
#     print(me.data)
#     add_user(me.data)
#     session['is_admin'] = False
#     if me.data['id'] and me.data['name'] and me.data['email']:
#         session['user'] = me.data
#         if me.data['email'] in config.ADMINS:
#             session['is_admin'] = True
#         return redirect(url_for('bp.tag', q='tag'))
#     else:
#         return "Login failed"


# @facebook.tokengetter
# def get_facebook_oauth_token():
#     return session.get('oauth_token')


# @bp.route('/fb-login')
# def fb_login():
#     """
#     The facebook login page. Clears the session before allowing a new user to authenticate.
#     """
#     print("login attempt")
#     session.clear()
#     print(request.args.get('next'))
#     return facebook.authorize(callback=url_for('bp.facebook_authorized',
#                                                next=request.args.get('next') or request.referrer or None,
#                                                _external=True))

###########################------Facebook Login Ends Here------#################################

@bp.route('/')
def index():
    return redirect(url_for('bp.login'))

@bp.route('/login', methods=['POST', 'GET'])
def login():
    my_logger.info("Login page hit with session data {}".format(session))
    if 'user' in session:
        return redirect(url_for('bp.tag', q='tag'))
    return render_template('login.htm')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp.login'))

@bp.route('/tagging', methods=['POST', 'GET'])
def tag():
    if 'user' in session:
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        q = request.args.get('q') 
        
        if (not session['is_admin']) and (q == 'verify' or q == '3-skips'):
            flash('Invalid credentials', 'error')
            return redirect(url_for('bp.login'))
        
        price_range_text_list = config.PRICE_RANGE_TEXT_LIST
        price_range_value_list = config.PRICE_RANGE_VALUE_LIST

        return render_template('tag_product.html',
                               vendors=get_vendors(),
                               available_cats=get_cat_list( "dc", "HQ-Data" ),
                               price_range_text_list=price_range_text_list,
                               price_range_value_list=price_range_value_list,
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count,
                               q=q,
                               autoescape=False)
    else:
        return redirect(url_for('bp.login'))


@bp.route('/cat-subcat-tagging', methods=['GET', 'POST'])
def cat_subcat_tagging():
    try:
        if 'user' in session:
            submit_status = "None"
            if request.form and request.method == "POST":
                form_cat = request.form.get("cat", "-1")
                form_subcat = request.form.get("subcat", "-1")
                if form_cat != "-1" and form_subcat != '-1':
                    hq_db.products.update({"product_name":request.form["hq-product"]}, {"$set":{"new_cat":form_cat, "new_subcat":form_subcat}})
                    submit_status = "Success"
                else:
                    submit_status = "Error"
            user_id = session['user']['id']
            tag_count, verify_count = get_tag_count(user_id)
            untagged_count = hq_db.products.find({"new_cat":{"$exists":False}}).count()
            product_name = None
            while untagged_count:
                rand_no = randint(0, untagged_count)
                cur = hq_db.products.find({"new_cat":{"$exists":False}}).limit(-1).skip(rand_no)
                product_dict = next(cur, None)
                if "product_name" in product_dict:
                    product_name = product_dict["product_name"]
                    break
            if product_name:
                all_products_finished = "False"
            else:
                all_products_finished = "True"
                product_name = "All products finished"
            return render_template("cat_subcat_tagging.html",
                                   username=session['user']['name'],
                                   tag_count=tag_count,
                                   verify_count=verify_count,
                                   hq_cats=get_hq_cat_list(),
                                   product=product_name,
                                   submit_status=submit_status,
                                   all_products_finished=all_products_finished
                                   )
        else:
            return redirect(url_for('bp.login'))
    except Exception as e:
        my_logger.error("Exception in cat_subcat_tagging function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in cat_subcat_tagging function",
            extra = {"Exception": e}
            )


@bp.route('/get-products', methods=['GET', 'POST'])
def get_products():
    try:
        posted_data = request.get_json()
        my_logger.info("Get products view hit with posted data = {}".format(posted_data))
        if 'price' in posted_data:
            posted_data['price'] = ast.literal_eval(posted_data['price'])
        q = posted_data.pop('q', None)

        if 'vendor' in posted_data and posted_data['vendor'] == 'All':
            posted_data.pop('vendor', None)
            
        if q == 'verify':
            tagging_info = get_product_tagging_details(posted_data, True)
        elif q == '3-skips':
            tagging_info = get_product_tagging_details(posted_data, False, True)
        else:
            tagging_info = get_product_tagging_details(posted_data)

        my_logger.info("Fetched product tagging info = {}".format(tagging_info))
        return json.dumps(tagging_info)
    except Exception as e:
        my_logger.error("Exception in get_products function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in get_products function",
            extra = {"Exception": e}
            )


@bp.route('/get-cats', methods=['GET', 'POST'])
def get_cats():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for getting categories = {}".format(posted_data))
        cat_cur = get_cat_list( posted_data["cat_filter"], posted_data["vendor"] )
        cat_list = []
        for cat in cat_cur:
            cat_list.append(cat)
        return to_json(cat_list)
    except Exception as e:
        my_logger.error("Exception in get_cats function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in get_cats function",
            extra = {"Exception": e}
            )

@bp.route('/get-subcats', methods=['GET', 'POST'])
def get_subcats():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for get sub-categories = {}".format(posted_data))
        return get_subcategories(posted_data['category_id'])
    except Exception as e:
        my_logger.error("Exception in get_subcats function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in get_subcats function",
            extra = {"Exception": e}
            )


@bp.route('/get-hq-subcats', methods=['GET', 'POST'])
def get_hq_subcats():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for get sub-categories = {}".format(posted_data))
        return get_hq_subcat_list(posted_data["cat"])
    except Exception as e:
        my_logger.error("Exception in get_hq_subcats function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in get_hq_subcats function",
            extra = {"Exception": e}
            )


@bp.route('/change-category', methods=['GET', 'POST'])
def change_category():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for change category = {}".format(posted_data))
        update_category(posted_data['id'], posted_data['category'], posted_data['subcat'])
        tag_list = get_taglist(posted_data['category'])
        tag_list.update(get_taglist(posted_data['subcat']))
        my_logger.info("Tag list after change category = {}".format(tag_list))
        return json.dumps(tag_list)
    except Exception as e:
        my_logger.error("Exception in change_category function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in change_category function",
            extra = {"Exception": e}
            )

@bp.route('/set-tags', methods=['GET', 'POST'])
def set_tags():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for set_tags function = {}".format(posted_data))
        q = posted_data.pop('q', None)
        id = posted_data.pop("id", None)
        user_id = session['user']['id']
        posted_data['tagged_by'] = user_id

        next_name = {}
        if 'category' in posted_data:
            next_name['category'] = posted_data.pop("category")
        if 'vendor_cat' in posted_data:
            next_name['vendor_cat'] = posted_data.pop('vendor_cat')
        if 'sub_category' in posted_data:
            next_name['sub_category'] = posted_data.pop('sub_category')
        if 'vendor_subcat' in posted_data:
            next_name['vendor_subcat'] = posted_data.pop('vendor_subcat')
        if 'vendor' in posted_data:
            vendor = posted_data.pop("vendor")
            if vendor != 'All':
                next_name['vendor'] = vendor
        if 'price' in posted_data:
            next_name['price'] = ast.literal_eval(posted_data.pop('price'))

        undo = posted_data.pop("undo", None)
        if undo:
            next_name.clear()
            next_name['_id'] = ObjectId(id)

        elif posted_data.pop("is_skipped"):
            inc_skip_count(id)

        else:
            my_logger.info("Tagged data to be saved after successful submit click = {}".format(posted_data))        
            db.products.update({'_id': ObjectId(id)}, {"$set": posted_data})
            inc_tag_count(user_id)

        #fetching next product tagging info
        tagging_info = get_product_tagging_details(next_name)

        if undo:
            db.products.update({'_id': ObjectId(id)},{"$unset":{'is_dirty':'', 'tags':'',
                                                        'tagged_by':'','epoch':''}})
            dcr_tag_count(user_id)

        tag_count, verify_count = get_tag_count(user_id)
        tagging_info['tag_count'] = tag_count
        tagging_info['verify_count'] = verify_count
        my_logger.info("Next product tagging info = {}".format(tagging_info))
        return json.dumps(tagging_info)
    except Exception as e:
        my_logger.error("Exception in set_tags function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in set_tags function",
            extra = {"Exception": e}
            )

@bp.route('/set-verified-tags', methods=['GET', 'POST'])
def set_verified_tags():
    try:
        posted_data = request.get_json()
        my_logger.info("Posted data for set_verified_tags function = {}".format(posted_data))
        q = posted_data.pop('q', None)
        id = posted_data.pop("id", None)
        user_id = session['user']['id']
        posted_data['verified_by'] = user_id
        posted_data['verified'] = True

        next_name = {}
        if 'category' in posted_data:
            next_name['category'] = posted_data.pop("category")
        if 'vendor_cat' in posted_data:
            next_name['vendor_cat'] = posted_data.pop('vendor_cat')
        if 'sub_category' in posted_data:
            next_name['sub_category'] = posted_data.pop('sub_category')
        if 'vendor_subcat' in posted_data:
            next_name['vendor_subcat'] = posted_data.pop('vendor_subcat')
        if 'vendor' in posted_data:
            vendor = posted_data.pop("vendor")
            if vendor != 'All':
                next_name['vendor'] = vendor
        if 'price' in posted_data:
            next_name['price'] = ast.literal_eval(posted_data.pop('price'))

        undo = posted_data.pop("undo", None)
        if undo:
            next_name.clear()
            next_name['_id'] = ObjectId(id)
            
        elif posted_data.pop("is_skipped"):
            admin_skip_keys = ['verified_by', 'verified', 'admin_tags']
            admin_skip_data = dict(map(lambda key: (key, posted_data.get(key, None)), admin_skip_keys))
            admin_skip_data['dirty_by_admin'] = True
            db.products.update({'_id': ObjectId(id)}, {"$set": admin_skip_data})
        
        else:
            my_logger.info("Verified data to be saved after successful submit click = {}".format(posted_data))
            db.products.update({'_id': ObjectId(id)}, {"$set": posted_data})
            inc_tag_count(user_id, True)

        #fetching next product tagging info
        if q == 'verify':
            tagging_info = get_product_tagging_details(next_name, True)
        elif q == '3-skips':
            tagging_info = get_product_tagging_details(next_name, False, True)

        if undo:
            db.products.update({'_id': ObjectId(id)},{"$unset":{'admin_tags':'','verified_by':'','verified':'','dirty_by_admin':''}})
            dcr_tag_count(user_id, True)

        tag_count, verify_count = get_tag_count(user_id)
        tagging_info['tag_count'] = tag_count
        tagging_info['verify_count'] = verify_count
        my_logger.info("Next product tagging info = {}".format(tagging_info))
        return json.dumps(tagging_info)
    except Exception as e:
        my_logger.error("Exception in set_verified_tags function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in set_verified_tags function",
            extra = {"Exception": e}
            )

@bp.route('/add-subcat', methods=['GET', 'POST'])
def add_subcat():
    try:
        if 'user' in session and session['is_admin']:
            subcat_status = 'Not Added'
            if request.form:
                if len(request.form['subcat']) and request.form['category'] != '-1':
                    subcat_status = add_new_subcat( request.form['category'], request.form['subcat'] )
                else:
                    subcat_status = 'Error'
                my_logger.info("Cat = {}, Subcat = {}, New subcat adding status = {}".format(request.form['category'], request.form['subcat'], subcat_status))
            user_id = session['user']['id']
            tag_count, verify_count = get_tag_count(user_id)
            return render_template("add_sub_cat.html",
                                   username=session['user']['name'],
                                   tag_count=tag_count,
                                   verify_count=verify_count,
                                   available_cats=get_cat_list( "dc", "HQ-Data" ),
                                   subcat_status=subcat_status)
        else:
            my_logger.error("Invalid credentials error with session = {}".format(session))
            flash('Invalid credentials', 'error')
            return redirect(url_for('bp.login'))
    except Exception as e:
        my_logger.error("Exception in add_subcat function, e = {}".format(e))
        sentry_client.captureException(
            message = "Exception in add_subcat function",
            extra = {"Exception": e}
            )


@bp.route('/leaderboard')
def view_leaderboard():
    if 'user' in session:
        my_logger.info("Leaderboard page hit")
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        return render_template("leaderboard.html",
                               users=get_users(),
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count)
    else:
        return redirect(url_for('bp.login'))

@bp.route('/tag-list')
def get_tags():
    if 'user' in session:
        my_logger.info("Tag-list page hit")
        user_id = session['user']['id']
        tag_count, verify_count = get_tag_count(user_id)
        return render_template("tag_list.html",
                               tags=get_all_tags(),
                               username=session['user']['name'],
                               tag_count=tag_count,
                               verify_count=verify_count)
    else:
        return redirect(url_for('bp.login'))


app.register_blueprint(bp, url_prefix='/cat-ui')
if __name__ == '__main__':
    app.debug = True
    app.run()
