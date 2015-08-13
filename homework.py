db = {
    'user':
        [
            {'id': 1, 'name': 'Chuck Norris', 'rate': 2},
            {'id': 2, 'name': 'Bruce Lee', 'rate': 1},
            {'id': 3, 'name': 'Jackie Chan', 'rate': 3},
        ]
}


class DBError(Exception):
    pass


class NotInDb(DBError):
    pass


class Field:
    _type = None
    _val = None
    _field_name = None
    _table_name = None

    def __init__(self, val=None):
        if val is None:
            return
        if isinstance(val, self._type):
            self._val = val
        else:
            raise ValueError

    def _set_field_name(self, name):
        self._field_name = name

    def __eq__(self, other):
        return ('"{self._table_name}"."{self._field_name}"'
                ' = \'{other}\''.format(**locals()))

    def __get__(self, instance, owner):
        self._table_name = owner.__tablename__
        if not instance:
            return self
        return self._val

    def __repr__(self):
        return str(self._val)


class TextField(Field):
    _type = str


class IntegerField(Field):
    _type = int


class Meta(type):

    def __new__(mcs, name, bases, attrs):
        if '__tablename__' in attrs:
            attrs.setdefault('id', IntegerField())
            fields = {}
            for k, v in filter(lambda x: isinstance(x[1], Field), attrs.items()):
                v._set_field_name(k)
                fields[k] = v
            attrs['_fields'] = fields

        return super(Meta, mcs).__new__(mcs, name, bases, attrs)


class Entity(metaclass=Meta):

    def __init__(self, save=True, **kwargs):
        kwargs.setdefault('id', self._get_id())
        self._check_fields(kwargs)

        for name, val in self._fields.items():
            value = val.__class__(kwargs[name])
            setattr(self, name, value)

        if save:
            self.save()

    def save(self):
        row = {name: getattr(self, name) for name in self._fields}
        table = self._get_table(self.__tablename__)
        table.append(row)

    def _get_id(self):
        table = self._get_table(self.__tablename__)
        last_id = max(row['id'] for row in table)
        return last_id + 1

    def _check_fields(self, kwargs):
        if set(self._fields.keys()) != set(kwargs.keys()):
            raise DBError("Fields don't much")

    @staticmethod
    def _get_table(table_name):
        table = db.get(table_name)
        if table is None:
            raise NotInDb('No such table in database')
        return table

    @classmethod
    def get(cls, _id):
        table = cls._get_table(cls.__tablename__)
        for row in table:
            if _id == row.get('id'):
                return cls(save=False, **row)
        raise NotInDb('No such id in table')

    def __repr__(self):
        return '{self.__class__} {self.name}'.format(self=self)


class User(Entity):
    __tablename__ = 'user'
    name = TextField()
    rate = IntegerField()


u = User.get(2)

u.name

u2 = User(name='Arni', rate=4)

u2.rate

s = User.name == 'Duncan MacLeod'

[print(x) for x in [u, u.name, u2, u2.rate, s]]