# The Type Object Pattern in Godot

This is all based on a chapter from [Game Programming Patterns](https://gameprogrammingpatterns.com/type-object.html) on a pattern called Type Object. I'm also using the same example Nystrom uses for his explanation of the pattern. Read his article about the pattern and  then come back to learn how I would implement it in Godot.

The idea is that instead of having a base class which contains some properties that are common to inherited classes, you move those properties into a different class which you then use to compose the classes that were previously obtaining the properties via inheritance.

The example they give is that you have a base Monster class and your game has a bunch of different breeds of monster. Each monster has a health value and an attack string. With the inheritance route, you can create a constructor which accepts those two properties, inherit from monster for a new breed, then the breed's constructor will call the base constructor with literals which define the properties. All properties are defined in code and since they are defined as literals, you can't serialize or deserialize the objects with different properties from like a plaintext or other structured data file.

Instead of going that route, you can have a Monster class which accepts a Breed in its constructor. Then when you create a monster, you pass a Breed object into the constructor and now the Monster is composed with a Breed. You can build those breed objects by any means, deserialize it from JSON or some custom format which makes it easier for someone not code-savvy to fiddle with the numbers.

Taking it further, you can construct a Monster using the Breed class's constructor and then passing in self as the breed to the Monster constructor. This is making use of the Factory Method Pattern. Now we can just construct a Breed and have a Monster as a result.

While a lot of the patterns in this book are geared towards a lower level of development than what we normally do in Godot, we can still apply this fairly effectively.

## The inheritance way

First, the anti-example where we do everything through inheritance.

Define a base class called monster which has a `health` and `attack_msg`, and a constructor to initialize them. We also define a `get_attack()` method which does nothing and a override to `_ready()` which prints the attack.

```gdscript
# monster.gd

class_name Monster extends RigidBody2D

var health: int = 0
var attack_msg: String = ""

func _init(_health: int, _attack_msg: String) -> void:
    self.health = _health
    self.attack_msg = _attack_msg

func _ready() -> void:
    print(get_attack())


func get_attack():
    pass

```

Next define a couple subclasses for a troll and a dragon

```gdscript
# troll.gd

extends Monster

func _init() -> void:
    super(20, "Die!")

func get_attack() -> String:
    return attack_msg

```

```gdscript
# dragon.gd

extends Monster

func _init() -> void:
    super(500, "Taste my fury!")

func get_attack() -> String:
    return attack_msg
```

All the subclasses do is call the base class's constructor to initialize the `health` and `attack_msg` and redefine override the `get_attack()` method.

The problem is that now we have to define a new script for every monster breed, extend the base class, and then finally implement all the custom stuff for the breed. Additionally, none of the properties have been exposed to the editor. We certainly could annotate the properties in the Monster class with @export, but this does nothing for our breeds. It will just show the default in the inspector and won't change the value if the default is updated, which will confuse everyone working on the project.

## The type object way

Instead, we want to attach the Monster script to all of our monster breeds. The Breed can then be defined using composition in a property on the Monster. Since Breed is now defining properties in an separate instance rather than through code, we can serialize the breed. This sounds a lot like Godot Resources.

First change the Monster class

```gdscript
# monster.gd
class_name Monster extends RigidBody2D

@export var breed: BreedResource

func _init(p_breed = null) -> void:
    breed = p_breed

func _ready() -> void:
    attack()

func attack() -> void:
    print(breed.get_attack())

```

Now it accepts a BreedResource in a breed exported property and calls `get_attack()` on the breed to attack.

Create a BreedResource:

```gdscript
#breed_resource.gd

class_name BreedResource extends Resource

@export var health: int
@export var attack_msg: String

func _init(p_health = 0, p_attack_msg = "") -> void:
    health = p_health
    attack_msg = p_attack_msg

func get_attack() -> String:
    return attack_msg
```

Now the resource is defining the fields.

When we attach the monster.gd script to a Node (in this case a RigidBody2D node), we can create a new Resource in the inspector and add the unique properties for the breed we are creating.

![Breed resource](/images/blog/godot-type-object-pattern/breed-resource.png)

Godot even handles the serialization and deserialization automatically with .tres files. For every breed we create, we can save a file to reuse and we can edit it as text:

```gdscript
# dragon.tres

[gd_resource type="Resource" script_class="BreedResource" load_steps=2 format=3 uid="uid://c6uypsr1qwjgj"]

[ext_resource type="Script" path="res://breed_resource.gd" id="1_6qihq"]

[resource]
script = ExtResource("1_6qihq")
health = 200
attack_msg = "Taste my fury!"
```

## Inheritance

I'm not sure how best to implement the parent breed that the book talks about. The way it works is that you can pass a parent Breed object to a breed and if the breed doesn't define a value for something like the health property, the parent will default it to a value. This is interesting in cases where you might have a minion breed that has a lot of sub-breeds, but they all have the same health.

You could do it exactly how the book describes by creating a parent sub-resource property on Breed of type Breed. Then, you can create a new resource for a minion with a set health value. Then, if the health of the breed with a minion parent is 0, the minion resource health would be the default.

The initial problem I notice is that, from the inspector, this relationship might not be very obvious. It probably won't be clear where the default health is coming from.

I think to make this a good way of handling this scenario would be only conditionally enabling the parent health setter in the inspector if the child health is not set. This way, it's more obvious that doing any changes to the parent health when the child has its health set already won't make any difference.

Anyway, you can do the basic inheritance like this:

```gdscript
# breed_resource.gd
class_name BreedResource extends Resource

@export var health: int
@export var attack_msg: String
@export var parent: BreedResource

func _init(p_health = 0, p_attack_msg = "", p_parent = null) -> void:
	health = p_health
	attack_msg = p_attack_msg
	parent = p_parent

func get_attack() -> String:
	return attack_msg

func get_health() -> int:
	if (health != 0 or parent == null):
		return health
	
	return parent.health
```

Notice the new exported property and the new `get_health()` method. Now we can add a new BreedResource as the parent in the inspector and if the health hasn't been set on the child, we default to the parent's health.

![Breed resource with parent](/images/blog/godot-type-object-pattern/breed-resource-with-parent.png)

You can see how it can be a bit confusing where the health value is coming from, but it does work.

The above code does have a little bug. If the monster has its health set directly and it has a parent with a non-zero health, we should sill prioritize our local health over the parent. However, if the local health goes to zero like when the monster is killed, the parent health will suddenly go into effect, giving the monster more health. We can solve this issue by updating the local health in the parent property setter and returning the local health from the `get_health()` method

```gdscript
# breed_resource.gd

class_name BreedResource extends Resource

@export var health: int
@export var attack_msg: String

@export var parent: BreedResource:
    set(value):
        if (health == 0 && value != null):
            health = value.health
        parent = value

func _init(p_health = 0, p_attack_msg = "", p_parent = null) -> void:
    health = p_health
    attack_msg = p_attack_msg
    parent = p_parent


func get_attack() -> String:
    return attack_msg

func get_health() -> int:
    return health
    
```

## Conclusion

In the end, Godot's resource system lends itself very well to the Type Object pattern. The inheritance part of it can get a little confusing from the inspector, but if we follow best practices and keep our inheritance tree shallow, simply remembering the rules should work well enough.