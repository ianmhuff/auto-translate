# autotranslate.py
This script should hopefully make the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing you to focus on just cleaning up the logic.

## Usage
Place auto-translate.py in the same directory as the files containing the scripts to be translated.

**==== CAUTION ====**  
The script will (should) indiscriminately and irrevocably modify any .txt, .c, or .rs files it finds in the directory it is run in. I might add some kind of additional safety/guardrails later but for now there is nothing else. I also make no guarantees that there isn't something, like, horribly wrong with the implementation of searching for files.

## List of modifications
- Changes indentation from 2 to 4 spaces
- Formats function calls 
  - eg `app::lua_bind::WorkModule__is_flag_impl` to `WorkModule::is_flag`
- Formats function header 
  - eg `void __thiscall L2CFighterDonkey::status::FinalAttack_main(L2CFighterDonkey *this,L2CValue *return_value)` to `unsafe extern "C" fn donkey_finalattack_main(fighter: &mut L2CFighterCommon) -> L2CValue {`
- Comments out `goto` and `LAB:` lines
- Removes `_` from beginning of consts

- Removals: removes these strings entirely
  - `(L2CValue *)&`
  - `(L2CValue *)`
  - `(float)`, `(int)`, `(bool)`, `(long)`
  - `return_value_XX`
 
- Replacements: the following substrings are replaced with different substrings:
  - `__` -> `::`
  - `this` -> `fighter/weapon` (depending on script type)
  - `->moduleAccessor` -> `.module_accessor`
  - `->globalTable` -> `.global_table`
  - `->luaStateAgent` -> `.lua_state_agent`
  - `lib::L2CValue::as_[type](var1)` -> `var1`

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

- Misc:
  - `lib::L2CValue::~L2CValue(var1);` -> `// free(var1);`
  - `lib::L2CValue::L2CValue(var1,var2);` -> `var1 = var2;`

## Example
Here's a small sample of what the output looks like: (OUTDATED, v0.5)

Original:
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

Output:
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
