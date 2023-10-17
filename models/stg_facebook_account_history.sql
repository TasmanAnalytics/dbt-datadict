with

source as (

    select * from {{ source('facebook_ads_fivetran', 'account_history') }}

),

renamed as (

    select
        id as account_id,
        name as account_name,
        case
            when account_name = 'Paired - App' then 'app'
            when account_name = 'Paired - Web' then 'web'
            else 'unknown'
        end as platform,
        currency as currency,
        _fivetran_synced as valid_from,
        lead(_fivetran_synced) over (partition by id order by _fivetran_synced) as valid_to

    from source

)

select * from renamed