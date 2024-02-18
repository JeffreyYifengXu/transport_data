# Importing the Flask Framework

from modules import *
from flask import *
import database
import configparser


# appsetup

page = {}
session = {}

# Initialise the FLASK application
app = Flask(__name__)
app.secret_key = 'SoMeSeCrEtKeYhErE'


# Debug = true if you want debug output on error ; change to false if you dont
app.debug = True


# Read my unikey to show me a personalised app
config = configparser.ConfigParser()
config.read('config.ini')
dbuser = config['DATABASE']['user']
portchoice = config['FLASK']['port']
if portchoice == '5xxx':
    print('ERROR: Please change config.ini as in the comments or Lab 08 instructions')
    exit(0)
session['isadmin'] = False

###########################################################################################
###########################################################################################
####                                 Database operative routes                         ####
###########################################################################################
###########################################################################################



#####################################################
##  INDEX
#####################################################

# What happens when we go to our website
@app.route('/')
def index():
    # If the user is not logged in, then make them go to the login page
    if( 'logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    page['username'] = dbuser
    page['title'] = 'Welcome'
    return render_template('welcome.html', session=session, page=page)

#####################################################
# User Login related                        
#####################################################
# login
@app.route('/login', methods=['POST', 'GET'])
def login():
    page = {'title' : 'Login', 'dbuser' : dbuser}
    # If it's a post method handle it nicely
    if(request.method == 'POST'):
        # Get our login value
        val = database.check_login(request.form['userid'], request.form['password'])
        print(val)
        print(request.form)
        # If our database connection gave back an error
        if(val == None):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('login'))

        # If it's null, or nothing came up, flash a message saying error
        # And make them go back to the login screen
        if(val is None or len(val) < 1):
            flash('There was an error logging you in')
            return redirect(url_for('login'))
        # If it was successful, then we can log them in :)
        print(val[0])
        session['name'] = val[0]['firstname']
        session['userid'] = request.form['userid']
        session['logged_in'] = True
        session['isadmin'] = val[0]['isadmin']
        return redirect(url_for('index'))
    else:
        # Else, they're just looking at the page :)
        if('logged_in' in session and session['logged_in'] == True):
            return redirect(url_for('index'))
        return render_template('index.html', page=page)

# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You have been logged out')
    return redirect(url_for('index'))



########################
#List All Items#
########################

@app.route('/users')
def list_users():
    '''
    List all rows in users by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_listdict = database.list_users()

    # Handle the null condition
    if (users_listdict is None):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users')
    page['title'] = 'List Contents of users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)
    

########################
#List Single Items#
########################


@app.route('/users/<userid>')
def list_single_users(userid):
    '''
    List all rows in users that match a particular id attribute userid by calling the 
    relevant database calls and pushing to the appropriate template
    '''

    # connect to the database and call the relevant function
    users_listdict = None
    users_listdict = database.list_users_equifilter("userid", userid)

    # Handle the null condition
    if (users_listdict is None or len(users_listdict) == 0):
        # Create an empty list and show error message
        users_listdict = []
        flash('Error, there are no rows in users that match the attribute "userid" for the value '+userid)
    page['title'] = 'List Single userid for users'
    return render_template('list_users.html', page=page, session=session, users=users_listdict)


########################
#List Search Items#
########################

@app.route('/consolidated/users')
def list_consolidated_users():
    '''
    List all rows in users join userroles 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    users_userroles_listdict = database.list_consolidated_users()

    # Handle the null condition
    if (users_userroles_listdict is None):
        # Create an empty list and show error message
        users_userroles_listdict = []
        flash('Error, there are no rows in users_userroles_listdict')
    page['title'] = 'List Contents of Users join Userroles'
    return render_template('list_consolidated_users.html', page=page, session=session, users=users_userroles_listdict)

@app.route('/user_stats')
def list_user_stats():
    '''
    List some user stats
    '''
    # connect to the database and call the relevant function
    user_stats = database.list_user_stats()

    # Handle the null condition
    if (user_stats is None):
        # Create an empty list and show error message
        user_stats = []
        flash('Error, there are no rows in user_stats')
    page['title'] = 'User Stats'
    return render_template('list_user_stats.html', page=page, session=session, users=user_stats)

@app.route('/users/search', methods=['POST', 'GET'])
def search_users_byname():
    '''
    List all rows in users that match a particular name
    by calling the relevant database calls and pushing to the appropriate template
    '''
    if(request.method == 'POST'):

        fnamesearch = database.search_users_customfilter("firstname","~",request.form['searchterm'])
        print(fnamesearch)
        lnamesearch = database.search_users_customfilter("lastname","~",request.form['searchterm'])
        print(lnamesearch)
        
        users_listdict = None

        if((fnamesearch == None) and (lnamesearch == None)):
            errortext = "Error with the database connection."
            errortext += "Please check your terminal and make sure you updated your INI files."
            flash(errortext)
            return redirect(url_for('index'))
        if(((fnamesearch == None) and (lnamesearch == None)) or ((len(fnamesearch) < 1) and len(lnamesearch) < 1)):
            flash(f"No items found for searchterm: {request.form['searchterm']}")
            return redirect(url_for('index'))
        else:
            
            users_listdict = fnamesearch
            users_listdict.extend(lnamesearch)
            # Handle the null condition'
            print(users_listdict)
            if (users_listdict is None or len(users_listdict) == 0):
                # Create an empty list and show error message
                users_listdict = []
                flash('Error, there are no rows in users that match the searchterm '+request.form['searchterm'])
            page['title'] = 'Search for a User by name'
            return render_template('list_users.html', page=page, session=session, users=users_listdict)
            

    else:
        return redirect(url_for('/users'))
        
@app.route('/users/delete/<userid>')
def delete_user(userid):
    '''
    List all rows in stations join stationtypes 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    resultval = database.delete_user(userid)
    
    # users_listdict = database.list_users()

    # # Handle the null condition
    # if (users_listdict is None):
    #     # Create an empty list and show error message
    #     users_listdict = []
    #     flash('Error, there are no rows in stations_stationtypes_listdict')
    page['title'] = f'List users after user {userid} has been deleted'
    return redirect(url_for('list_consolidated_users'))
    
@app.route('/users/update', methods=['POST','GET'])
def update_user():
    """
    Update details for a user
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('userid' not in request.form):
            # should be an exit condition
            flash("Can not update without a userid")
            return redirect(url_for('list_users'))
        else:
            newdict['userid'] = request.form['userid']
            print("We have a value: ",newdict['userid'])

        if ('firstname' not in request.form):
            newdict['firstname'] = None
        else:
            validupdate = True
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = None
        else:
            validupdate = True
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = None
        else:
            validupdate = True
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = None
        else:
            validupdate = True
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_single_user(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values")
            return redirect(url_for('show_all_segment'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['startid'])
    else:
        return redirect(url_for('show_all_segment'))

######
## add items 
######

    
@app.route('/users/add', methods=['POST','GET'])
def add_user():
    """
    Add a new User
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Add user details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        
        if ('firstname' not in request.form):
            newdict['firstname'] = 'Empty firstname'
        else:
            newdict['firstname'] = request.form['firstname']
            print("We have a value: ",newdict['firstname'])

        if ('lastname' not in request.form):
            newdict['lastname'] = 'Empty lastname'
        else:
            newdict['lastname'] = request.form['lastname']
            print("We have a value: ",newdict['lastname'])

        if ('userroleid' not in request.form):
            newdict['userroleid'] = 1 # default is traveler
        else:
            newdict['userroleid'] = request.form['userroleid']
            print("We have a value: ",newdict['userroleid'])

        if ('password' not in request.form):
            newdict['password'] = 'blank'
        else:
            newdict['password'] = request.form['password']
            print("We have a value: ",newdict['password'])

        print('Insert parametesrs are:')
        print(newdict)

        database.add_user_insert(newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('list_consolidated_users'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_user.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())


#Show all travel segments
@app.route('/traveltimes/show_all_segment')
def show_all_segment():
    "Display all available travel segments"
    
    #List all travel segments
    showpath_listdict = database.show_all_path(1, None)

    # Handle the null condition
    if (showpath_listdict is None):
        # Create an empty list and show error message
        showpath_listdict = []
        flash('Error, there are no rows in showpath_listdict')
    page['title'] = 'All available travel segments'
    return render_template('show_all_segment.html', page=page, session=session, traveltimes=showpath_listdict)


@app.route('/traveltimes/show_specific_travel_path', methods=['POST', 'GET'])
def show_specific_travel_path():
    "Show specific travel path given specific number of stops"
       
    #List specific travel segments
    usr_input = str(request.form['searchterm'])
    showpath_listdict = database.show_all_path(0, usr_input)

    # Handle the null condition
    if (showpath_listdict is None):
        # Create an empty list and show error message
        showpath_listdict = []
        flash('Error, there are no rows in showpath_listdict')
    page['title'] = 'All available travel segments'
    return render_template('show_all_segment.html', page=page, session=session, traveltimes=showpath_listdict)



@app.route('/traveltimes/add_path_segment', methods=['POST', 'GET'])
def add_path_segment():
    """
    add a new path segment
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin
    page['title'] = 'Add path'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        
        if ('startstationid' not in request.form):
            newdict['startatationid'] = 'Not specified'
        else:
            newdict['startstationid'] = request.form['startstationid']
            print("We have a value: ",newdict['startstationid'])

        if ('endstationid' not in request.form):
            newdict['endstation'] = 'Not specified'
        else:
            newdict['endstationid'] = request.form['endstationid']
            print("We have a value: ",newdict['endstationid'])

        if ('expectedtraveltimeseconds' not in request.form):
            newdict['expectedtraveltimeseconds'] = 100 # default is traveler
        else:
            newdict['expectedtraveltimeseconds'] = request.form['expectedtraveltimeseconds']
            print("We have a value: ",newdict['expectedtraveltimeseconds'])

        if ('stopstraversed' not in request.form):
            newdict['stopstraversed'] = 1
        else:
            newdict['stopstraversed'] = request.form['stopstraversed']
            print("We have a value: ",newdict['stopstraversed'])
        
        if ('triplegs' not in request.form):
            newdict['triplegs'] = 1
        else:
            newdict['triplegs'] = request.form['triplegs']
            print("We have a value: ",newdict['triplegs'])

        if ('coordinatemaplen' not in request.form):
            newdict['coordinatemaplen'] = 1
        else:
            newdict['coordinatemaplen'] = request.form['coordinatemaplen']
            print("We have a value: ",newdict['coordinatemaplen'])


        print('Insert parametesrs are:')
        print(newdict)

        database.add_path_segment(newdict['startstationid'],newdict['endstationid'],newdict['expectedtraveltimeseconds'],newdict['stopstraversed'], newdict['triplegs'], newdict['coordinatemaplen'])
        # Should redirect to your newly updated user
        print("did it go wrong here?")
        return redirect(url_for('show_all_segment'))
    else:
        # assuming GET request, need to setup for this
        return render_template('add_path_segment.html',
                           session=session,
                           page=page,
                           userroles=database.list_userroles())


@app.route('/users/delete_path_segment/<startid>/<endid>')
def delete_path_segment(startid, endid):
    '''
    List all rows in stations join stationtypes 
    by calling the relvant database calls and pushing to the appropriate template
    '''
    # connect to the database and call the relevant function
    print("delete path segment is called")
    resultval = database.delete_path_segment(startid, endid)
    
    # users_listdict = database.list_users()

    # # Handle the null condition
    # if (users_listdict is None):
    #     # Create an empty list and show error message
    #     users_listdict = []
    #     flash('Error, there are no rows in stations_stationtypes_listdict')
    page['title'] = f'List path segments after path segment {startid, endid} has been deleted'
    return redirect(url_for('show_all_segment'))


@app.route('/traveltimes/update_path_segment', methods=['POST','GET'])
def update_path_segment():
    """
    Update details for a path segment
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    
    # Need a check for isAdmin

    page['title'] = 'Update path segment details'

    userslist = None
    print("request form is:")
    newdict = {}
    print(request.form)
    validupdate = False
    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('startstationid' not in request.form):
            # should be an exit condition
            flash("Can not update without a startstationid")
            return redirect(url_for('show_all_segment'))
        else:
            newdict['startstationid'] = request.form['startstationid']
            print("We have a value: ",newdict['startstationid'])

        if ('endstationid' not in request.form):
            newdict['endstationid'] = None
        else:
            validupdate = True
            newdict['endstationid'] = request.form['endstationid']
            print("We have a value: ",newdict['endstationid'])

        if ('expectedtraveltimeseconds' not in request.form):
            newdict['expectedtraveltimeseconds'] = None
        else:
            validupdate = True
            newdict['expectedtraveltimeseconds'] = request.form['expectedtraveltimeseconds']
            print("We have a value: ",newdict['lastname'])

        if ('stopstraversed' not in request.form):
            newdict['stopstraversed'] = None
        else:
            validupdate = True
            newdict['stopstraversed'] = request.form['stopstraversed']
            print("We have a value: ",newdict['stopstraversed'])

        if ('triplegs' not in request.form):
            newdict['triplegs'] = None
        else:
            validupdate = True
            newdict['triplegs'] = request.form['triplegs']
            print("We have a value: ",newdict['triplegs'])
        
        if ('coordinatemaplen' not in request.form):
            newdict['coordinatemaplen'] = None
        else:
            validupdate = True
            newdict['coordinatemaplen'] = request.form['coordinatemaplen']
            print("We have a value: ",newdict['coordinatemaplen'])

        print('Update dict is:')
        print(newdict, validupdate)

        if validupdate:
            #forward to the database to manage update
            userslist = database.update_(newdict['userid'],newdict['firstname'],newdict['lastname'],newdict['userroleid'],newdict['password'])
        else:
            # no updates
            flash("No updated values for user with userid")
            return redirect(url_for('list_users'))
        # Should redirect to your newly updated user
        return list_single_users(newdict['userid'])
    else:
        return redirect(url_for('list_consolidated_users'))


@app.route('/users/produce_report')
def produce_report():
    "Produce a report of all stations along with its longest traveltimes"
    
    #List all travel segments
    showpath_listdict = database.produce_report()

    # Handle the null condition
    if (showpath_listdict is None):
        # Create an empty list and show error message
        showpath_listdict = []
        flash('Error, there are no rows in showpath_listdict')
    page['title'] = 'Traveltimes report'
    return render_template('show_report.html', page=page, session=session, traveltimes=showpath_listdict)
    


