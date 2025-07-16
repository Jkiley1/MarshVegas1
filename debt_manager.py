class YieldCurve(): 
    def __init__(self):
        # self.name = name
        self.children = []

    """Define terms for cash flow up here
        maybe a enumerate function
    """
    def add_bond(self, child_name, **kwargs):
        """Arguments: 
            n: number of periods = None,
            nper: payments per period = None
            i: interest rate = None
            pmt: cash flows received (made) from (to) counterparty
            """
        return Bond(self, child_name, **kwargs)
    
    @property
    def get_children(self):
        return [child.name for child in self.children]

class Bond:
    def __init__(self, parent_instance, child_name, **kwargs):
        if not isinstance(parent_instance, YieldCurve):
            raise TypeError("Child instance must be created through Parent().create_child()")
        
        self.parent = parent_instance
        self.name = child_name
        self.test = None
        parent_instance.children.append(self)

        # Start of the key, value class attributes
        self.market_price = kwargs.get('market_price')
        print(self.market_price)
    def give_me_a_new_name_son_I_deserve_it_fr_fr(self, child_name):
        self.name = child_name
    
    def define_void(self, void):
        self.test = void
        
parent = YieldCurve()
child = parent.add_bond('yes', market_price = 4)

"""
    ** Ding! **

Standing before
    this bur'ned land

A place of untold
    cruelty

The vultures a-wait
    the dinner bell

Its Chime; 

The blaring, bleating


    ** Ding! **
Longing

spawner at -28, -7, 814
"""