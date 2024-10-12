This script should hopefully make the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing you to focus on just cleaning up the logic.

The script will also keep code on the same line it started on; i.e. if a particular bit of code is on line 57 in the original, it will still be on line 57 when the script is done. That way, any lines of code that need additional work can be easily investigated by comparing against the original code.

I also left in the tilde lines as comments reformatted as `// free(var)` since I sometimes find them helpful for following the logic of the script.

I'm not a Python expert by any means so this code is probably pretty inefficient, but it works for now at the very least.

How to use:

Place auto-translate.py in the same directory as the files containing the scripts to be translated.


==== CAUTION ====

The script will (should) indiscriminately and irrevocably modify any .txt, .c, or .rs files it finds in the directory it is run in. I might add some kind of additional safety/guardrails later but for now there is nothing else. I also make no guarantees that there isn't something, like, horribly wrong with the implementation of searching for files.

List of modifications:
- Removals: the following substrings are replaced with "" on all lines:
  - `(L2CValue *)&`
  - `(L2CValue *)`
  - `app::lua_bind::`
  - `_impl`
  - `return_value_xx`
 
- Replacements: the following substrings are removed and replaced with different substrings:
  - `__` -> `::`
  - `this->moduleAccessor` -> `fighter.module_accessor`
  - `this->globalTable` -> `fighter.global_table`

- Operators: lines containing the following "operator" functions are restructured:
  - `lib::L2CValue::operator[op](var1,var2,var3)` -> `var3 = var1 [op] var2`
  - `lib::L2CValue::operator=(var1,var2)` -> `var1 = var2`
  - `lib::L2CValue::operator[](var1,var2)` -> `var1[var2]`
  - `lib::L2CValue::operator[op](var1,var2)` -> `var1 [op] var2`
 
- If Statements: the conditions of if statements are simplified:
  - `if ((var1 & 1) != 0)` -> `if var1`
  - `if ((var1 & 1) == 0)` -> `if !var1`
  - `if ((var1 & 1U) != 0)` -> `if var1`
  - `if ((var1 & 1U) == 0)` -> `if !var1`

- As Type: the following as_(type)s are simplified:
  - `lib::L2CValue::as_integer(var1)` -> `var1`
  - `lib::L2CValue::as_hash(var1)` -> `var1`
  - `lib::L2CValue::as_bool(var1)` -> `var1`

- Misc:
  - `(bool)(var1 & 1)` -> `var1`
  - `lib::L2CValue::L2CValue(var1,var2);` -> `var1 = var2;`
  - `lib::L2CValue::~L2CValue(var1);` -> `// free(var1);`


Here's a small sample of what the output looks like:

original:
```
{
  lib::L2CValue::L2CValue(aLStack96,_FIGHTER_YOSHI_STATUS_SPECIAL_HI_FLAG_EGG_APPEAR);
  iVar2 = lib::L2CValue::as_integer(aLStack96);
  app::lua_bind::WorkModule__off_flag_impl(this->moduleAccessor,iVar2);
  lib::L2CValue::~L2CValue(aLStack96);
  lib::L2CValue::L2CValue(aLStack96,_FIGHTER_YOSHI_STATUS_SPECIAL_HI_FLAG_EGG_SHOOT);
  iVar2 = lib::L2CValue::as_integer(aLStack96);
  app::lua_bind::WorkModule__off_flag_impl(this->moduleAccessor,iVar2);
  lib::L2CValue::~L2CValue(aLStack96);
  lib::L2CValue::L2CValue(aLStack96,0);
  lib::L2CValue::L2CValue(aLStack112,_FIGHTER_YOSHI_STATUS_SPECIAL_HI_WORK_INT_EGG_COUNT);
  iVar2 = lib::L2CValue::as_integer(aLStack96);
  iVar3 = lib::L2CValue::as_integer(aLStack112);
  app::lua_bind::WorkModule__set_int_impl(this->moduleAccessor,iVar2,iVar3);
  lib::L2CValue::~L2CValue(aLStack112);
  lib::L2CValue::~L2CValue(aLStack96);
  pLVar5 = (L2CValue *)lib::L2CValue::operator[]((L2CValue *)&this->globalTable,0x16);
  lib::L2CValue::L2CValue(aLStack96,_SITUATION_KIND_GROUND);
  uVar6 = lib::L2CValue::operator==(pLVar5,aLStack96);
  lib::L2CValue::~L2CValue(aLStack96);
  if ((uVar6 & 1) == 0) {
    lib::L2CValue::L2CValue(aLStack96,0xed8a31e01);
    lib::L2CValue::L2CValue(aLStack112,0.0,return_value_02);
    lib::L2CValue::L2CValue(aLStack128,1.0,return_value_03);
    lib::L2CValue::L2CValue(aLStack144,false);
    HVar7 = lib::L2CValue::as_hash(aLStack96);
    fVar8 = (float)lib::L2CValue::as_number(aLStack112);
    fVar9 = (float)lib::L2CValue::as_number(aLStack128);
    bVar1 = lib::L2CValue::as_bool(aLStack144);
    app::lua_bind::MotionModule__change_motion_impl
              (this->moduleAccessor,HVar7,fVar8,fVar9,(bool)(bVar1 & 1),0.0,false,false);
    lib::L2CValue::~L2CValue(aLStack144);
    lib::L2CValue::~L2CValue(aLStack128);
    lib::L2CValue::~L2CValue(aLStack112);
  }
}
```

output:
```
{
  aLStack96 = _FIGHTER_YOSHI_STATUS_SPECIAL_HI_FLAG_EGG_APPEAR;
  iVar2 = aLStack96;
  WorkModule::off_flag(fighter.module_accessor,iVar2);
  // free(aLStack96);
  aLStack96 = _FIGHTER_YOSHI_STATUS_SPECIAL_HI_FLAG_EGG_SHOOT;
  iVar2 = aLStack96;
  WorkModule::off_flag(fighter.module_accessor,iVar2);
  // free(aLStack96);
  aLStack96 = 0;
  aLStack112 = _FIGHTER_YOSHI_STATUS_SPECIAL_HI_WORK_INT_EGG_COUNT;
  iVar2 = aLStack96;
  iVar3 = aLStack112;
  WorkModule::set_int(fighter.module_accessor,iVar2,iVar3);
  // free(aLStack112);
  // free(aLStack96);
  pLVar5 = fighter.global_table[0x16];
  aLStack96 = _SITUATION_KIND_GROUND;
  uVar6 = pLVar5 == aLStack96;
  // free(aLStack96);
  if !uVar6 {
    aLStack96 = 0xed8a31e01;
    aLStack112 = 0.0;
    aLStack128 = 1.0;
    aLStack144 = false;
    HVar7 = aLStack96;
    fVar8 = (float)lib::L2CValue::as_number(aLStack112);
    fVar9 = (float)lib::L2CValue::as_number(aLStack128);
    bVar1 = aLStack144;
    MotionModule::change_motion
              (fighter.module_accessor,HVar7,fVar8,fVar9,bVar1,0.0,false,false);
    // free(aLStack144);
    // free(aLStack128);
    // free(aLStack112);
  }
}
```
