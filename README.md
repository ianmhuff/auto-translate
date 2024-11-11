# Auto-Translate
This python script makes the process of translating SSBU status scripts a little less tedious by automatically performing many of the more basic steps, allowing the user to focus on just cleaning up the logic.

## Usage
#### Every file in the folder
1. Place `autotranslate.py` in the same directory as the files containing the scripts to be translated (one script per file)
2. Click on `autotranslate.py` or run it in the console with `python autotranslate.py` to automatically translate any files found in the current folder
---
#### Only select files
1. Drag files of any type (one script per file) onto `autotranslate.py` to translate them

## List of modifications
- Changes indentation from 2 to 4 spaces
- Formats function calls (eg `app::lua_bind::WorkModule__is_flag_impl` to `WorkModule::is_flag`)
- Formats function header (eg `void __thiscall L2CFighterDonkey::status::FinalAttack_main(L2CFighterDonkey *this,L2CValue *return_value)` to `unsafe extern "C" fn donkey_finalattack_main(fighter: &mut L2CFighterCommon) -> L2CValue {`)
- Comments out `goto` and `LAB:` lines
- Removes `_` from beginning of consts
- Removes all data type conversions (eg `(int)`, `(long)`, `(L2CValue *)`)
- Removes `return_value_XX`
- Translates hashes
- Reformats `change_status`, `sub_shift_status_main`/`fastshift`, `Vector3::create`, and `lerp`
- Reformats all `L2CFighterCommon` functions
- Reformats `clear`, `push`, and `pop` for `lua_stack`s
- Reformats returns
- Reformats `main_loop` function names used in `sub_shift_status_main` calls
- Optionally renames the file once completed
 
- Replacements: the following substrings are replaced with different substrings:
  - `__` -> `::`
  - `this` -> `fighter/weapon` (depending on script type)
  - `->moduleAccessor` -> `.module_accessor`
  - `->globalTable` -> `.global_table`
  - `->luaStateAgent` -> `.lua_state_agent`
  - `lib::L2CValue::as_[type](var1)` -> `var1`
  - `lib::L2CValue::operator.cast.to.bool(aLStackXX)` -> `aLStackXX`
  - `lib::L2CValue::L2CValue(var1,var2);` -> `var1 = var2;`

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

## autotranslate_settings.ini
```ini
[General]
keep_tilde_lines =# Whether to reformat lines with tildes or remove them entirely
keep_var_declarations =# Whether to keep the section of variable declarations at the top of the file or not

[FileHandling]
search_file_types =# List of file types to look for in the current directory 
output_file_type =# File type to output in
output_file_name =# Whether to [keep] the original file name when outputting or [rename] to the function name
path_to_param_labels =# Filepath to ParamLabels.csv

[Development]
condense_script =# Whether to enable the experimental script condenser feature
```

## Example
Here's a small sample of what the output looks like: **(v0.9.0)**

Original:
```

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
L2CFighterDonkey::status::FinalAttack_main(L2CFighterDonkey *this,L2CValue *return_value)

{
  byte bVar1;
  int iVar2;
  L2CValue *this_00;
  ulong uVar3;
  Hash40 HVar4;
  float fVar5;
  float fVar6;
  L2CValue aLStack128 [16];
  L2CValue aLStack112 [16];
  L2CValue aLStack96 [16];
  L2CValue aLStack80 [16];
  
  lib::L2CValue::L2CValue(aLStack80,false);
  bVar1 = lib::L2CValue::as_bool(aLStack80);
  app::lua_bind::AreaModule__set_whole_impl(this->moduleAccessor,(bool)(bVar1 & 1));
  lib::L2CValue::~L2CValue(aLStack80);
  this_00 = (L2CValue *)lib::L2CValue::operator[]((L2CValue *)&this->globalTable,0x16);
  lib::L2CValue::L2CValue(aLStack80,_SITUATION_KIND_GROUND);
  uVar3 = lib::L2CValue::operator==(this_00,aLStack80);
  lib::L2CValue::~L2CValue(aLStack80);
  if ((uVar3 & 1) == 0) {
    lib::L2CValue::L2CValue(aLStack80,0x10e315f739);
    lib::L2CValue::L2CValue(aLStack96,0.0);
    lib::L2CValue::L2CValue(aLStack112,1.0);
    lib::L2CValue::L2CValue(aLStack128,false);
    HVar4 = lib::L2CValue::as_hash(aLStack80);
    fVar5 = (float)lib::L2CValue::as_number(aLStack96);
    fVar6 = (float)lib::L2CValue::as_number(aLStack112);
    bVar1 = lib::L2CValue::as_bool(aLStack128);
    app::lua_bind::MotionModule__change_motion_impl
              (this->moduleAccessor,HVar4,fVar5,fVar6,(bool)(bVar1 & 1),0.0,false,false);
  }
  else {
    lib::L2CValue::L2CValue(aLStack80,0xcb7cea62c);
    lib::L2CValue::L2CValue(aLStack96,0.0);
    lib::L2CValue::L2CValue(aLStack112,1.0);
    lib::L2CValue::L2CValue(aLStack128,false);
    HVar4 = lib::L2CValue::as_hash(aLStack80);
    fVar5 = (float)lib::L2CValue::as_number(aLStack96);
    fVar6 = (float)lib::L2CValue::as_number(aLStack112);
    bVar1 = lib::L2CValue::as_bool(aLStack128);
    app::lua_bind::MotionModule__change_motion_impl
              (this->moduleAccessor,HVar4,fVar5,fVar6,(bool)(bVar1 & 1),0.0,false,false);
  }
  lib::L2CValue::~L2CValue(aLStack128);
  lib::L2CValue::~L2CValue(aLStack112);
  lib::L2CValue::~L2CValue(aLStack96);
  lib::L2CValue::~L2CValue(aLStack80);
  lib::L2CValue::L2CValue(aLStack80,_FIGHTER_KINETIC_ENERGY_ID_STOP);
  iVar2 = lib::L2CValue::as_integer(aLStack80);
  app::lua_bind::KineticModule__enable_energy_impl(this->moduleAccessor,iVar2);
  lib::L2CValue::~L2CValue(aLStack80);
  lib::L2CValue::L2CValue(aLStack80,_FIGHTER_KINETIC_ENERGY_ID_GROUND_MOVEMENT);
  iVar2 = lib::L2CValue::as_integer(aLStack80);
  app::lua_bind::KineticModule__unable_energy_impl(this->moduleAccessor,iVar2);
  lib::L2CValue::~L2CValue(aLStack80);
  FUN_710000cc50(this);
  lib::L2CValue::L2CValue(aLStack80,FinalAttack_main_loop);
  lua2cpp::L2CFighterCommon::sub_shift_status_main(this,(L2CValue)0xb0,return_value);
  lib::L2CValue::~L2CValue(aLStack80);
  return;
}
```

Output:
```rs
unsafe extern "C" fn donkey_finalattack_main(fighter: &mut L2CFighterCommon) -> L2CValue {
    aLStack80 = false;
    bVar1 = aLStack80;
    AreaModule::set_whole(fighter.module_accessor, bVar1);
    this_00 = fighter.global_table[0x16];
    aLStack80 = SITUATION_KIND_GROUND;
    uVar3 = this_00 == aLStack80;
    if !uVar3 {
        aLStack80 = Hash40::new("final_air_attack");
        aLStack96 = 0.0;
        aLStack112 = 1.0;
        aLStack128 = false;
        HVar4 = aLStack80;
        fVar5 = aLStack96;
        fVar6 = aLStack112;
        bVar1 = aLStack128;
        MotionModule::change_motion(fighter.module_accessor, HVar4, fVar5, fVar6, bVar1, 0.0, false, false);
    } else {
        aLStack80 = Hash40::new("final_attack");
        aLStack96 = 0.0;
        aLStack112 = 1.0;
        aLStack128 = false;
        HVar4 = aLStack80;
        fVar5 = aLStack96;
        fVar6 = aLStack112;
        bVar1 = aLStack128;
        MotionModule::change_motion(fighter.module_accessor, HVar4, fVar5, fVar6, bVar1, 0.0, false, false);
    }
    aLStack80 = FIGHTER_KINETIC_ENERGY_ID_STOP;
    iVar2 = aLStack80;
    KineticModule::enable_energy(fighter.module_accessor, iVar2);
    aLStack80 = FIGHTER_KINETIC_ENERGY_ID_GROUND_MOVEMENT;
    iVar2 = aLStack80;
    KineticModule::unable_energy(fighter.module_accessor, iVar2);
    FUN_710000cc50(fighter);
    aLStack80 = FinalAttack_main_loop;
    fighter.sub_shift_status_main(L2CValue::Ptr(0xb0 as *const () as _));
    return;
}
```

Output (with **v0.9.0**'s experimental `condense_script` feature):
```rs
unsafe extern "C" fn donkey_finalattack_main(fighter: &mut L2CFighterCommon) -> L2CValue {
    AreaModule::set_whole(fighter.module_accessor, false);
    if fighter.global_table[0x16] != *SITUATION_KIND_GROUND {
        MotionModule::change_motion(fighter.module_accessor, Hash40::new("final_air_attack"), 0.0, 1.0, false, 0.0, false, false);
    } else {
        MotionModule::change_motion(fighter.module_accessor, Hash40::new("final_attack"), 0.0, 1.0, false, 0.0, false, false);
    }
    KineticModule::enable_energy(fighter.module_accessor, *FIGHTER_KINETIC_ENERGY_ID_STOP);
    KineticModule::unable_energy(fighter.module_accessor, *FIGHTER_KINETIC_ENERGY_ID_GROUND_MOVEMENT);
    FUN_710000cc50(fighter);
    fighter.sub_shift_status_main(L2CValue::Ptr(donkey_finalattack_main_loop as *const () as _))
}
```